import base64
import os
import os.path
import re
from six.moves import input
import tempfile
import yaml

from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.api_lib.deployment_manager import dm_api_util
from googlecloudsdk.api_lib.deployment_manager import dm_base
from googlecloudsdk.api_lib.deployment_manager import exceptions as dm_exceptions
from googlecloudsdk.command_lib.deployment_manager import dm_util
from googlecloudsdk.command_lib.deployment_manager import dm_write
from googlecloudsdk.command_lib.deployment_manager import flags
from googlecloudsdk.command_lib.deployment_manager.importer import BuildConfig
from googlecloudsdk.command_lib.deployment_manager.importer import BuildTargetConfig
from googlecloudsdk.core.resource import resource_printer
from googlecloudsdk.third_party.apis.deploymentmanager.v2 import deploymentmanager_v2_messages as messages
import jinja2
from cloud_foundation_toolkit import LOG
from cloud_foundation_toolkit.dm_utils import DM_API, get_deployment


def run(paths):
    config = Config(paths)
    for i in config:
        LOG.debug('===> %s', i.rendered)
        deployment = Deployment(i)
        try:
            deployment.create()
        except apitools_exceptions.HttpConflictError as err:
            deployment.update()


def ask():
    answer = input("Update(u), Skip (s), or Abort(a) Deployment? ")
    if answer in ['u', 's', 'a']:
        return answer
    ask()


class ConfigFile(object):
    """ Class representing a CFT config item """

    def __init__(self, path):
        """ Contructor

        Args:
            path (str): The path to a config file
        """

        self.path = path

        with open(path) as f:
            self.raw = f.read()

        self.rendered = jinja2.Template(self.raw).render()


class Config(object):
    """ A container Class for CFT config files

    This class holds ConfigFile() objects. For all intents and purposes
    it's a list().

    """

    def __init__(self, paths):
        """ Contructor

        Args:
            paths (str): The paths to the CFT configs.
                paths can be a list of files, a directory, or wildcards
                such as "*", or "/some/dir/prod*". In the case of
                wildcards, only files with extentions ".yaml", ".yml"
                and ".jinja" are matched

        """

        self._items = [ConfigFile(path) for path in paths]
        self.sort()

    def __iter__(self):
        """ This makes the class behave like a list """
        return iter(self._items)


    def sort(self):
        """ Sorts the deployments based on the dependency graph"""
        pass



class Deployment(DM_API):
    """ Class representing a deployment """

    # Number of seconds to wait for a create/update/delete operation
    OPERATION_TIMEOUT = 20 * 60 # 20 mins. Same as gcloud

    # The keys required by a DM config (not CFT config)
    DM_CONFIG_KEYS = ['imports', 'resources', 'outputs']

    def __init__(self, config_file):
        """ The class constructor

        Args:
            config_item (configItem): A dict representing CFT config.
                Normally provided when creating/updating a deployment.
        """

        # This is here to avoid circular imports
        from cloud_foundation_toolkit.yaml_utils import DMYamlLoader # pylint: disable=g-import-not-at-top, circular dependency

#        self.config_file = config_file
#        self.fingerprint = None

        # Resolve custom yaml tags only during deployment instantiation
        # because if parsed before, the DM queries implemented for the
        # tags would likely fail with 404s
        self.config = yaml.load(
            config_file.rendered,
            Loader=DMYamlLoader
        )
        self.config['project'] = self.config.get(
            'project',
            dm_base.GetProject()
        )
        LOG.debug('==> %s', self.config)
        self.current = None

    @property
    def dm_config(self):
        """
        TODO (gus): Could a dictview be used here?
        """

        return {
            k: v for k, v in self.config.items() if k in self.DM_CONFIG_KEYS
        }

    @property
    def target_config(self):
        self.write_tmp_file()
        target = BuildTargetConfig(messages, config=self.tmp_file_path)
        self.delete_tmp_file()
        return target

#    def get_fingerprint(self):
#        """ Returns the fingerprint of a deployment in DM """
#        fingerprint = dm_api_util.FetchDeploymentFingerprint(
#            self.client,
#            self.messages,
#            self.config['project'],
#            self.config['name']
#        )
#        return base64.urlsafe_b64encode(fingerprint)

    def render(self, content=None):
        """ Returns a yaml dump of the deployment"""
        content = content or self.dm_config
        return yaml.dump(content, indent=2)


    def write_tmp_file(self):
        """ Writes the yaml dump of the deployment to a temp file"""

        with tempfile.NamedTemporaryFile(dir=os.getcwd(), delete=False) as tmp:
            tmp.write(self.render())
            self.tmp_file_path = tmp.name

    def delete_tmp_file(self):
        os.remove(self.tmp_file_path)


    def get(self):
        """ Returns a Deployment() message(obj) from the DM API """

        try:
            self.current = self.client.deployments.Get(
                self.messages.DeploymentmanagerDeploymentsGetRequest(
                    project=self.config['project'],
                    deployment=self.config['name']
                )
            )
        except apitools_exceptions.HttpNotFoundError as _:
            self.current = None
        return self.current

    def sync(self):
        return self.get()

    def create(self, preview=False):
        """ Creates this deployment in DM """

        deployment = self.messages.Deployment(
            name=self.config['name'],
            target=self.target_config
        )
        request = self.messages.DeploymentmanagerDeploymentsInsertRequest(
            deployment=deployment,
            project=self.config['project'],
            preview=preview
#            createPolicy='CREATE_OR_ACQUIRE'
        )
        LOG.debug(
            'Creating deployment %s with data %s',
            self.config['name'],
            request
        )

        # The actual update.
        # No exception handling is done here to allow higher level
        # functions to do so
        operation = self.client.deployments.Insert(request)

        # Fetch and print the latest fingerprint of the deployment.
        self.get()

        # Wait for operation to finish
        self.wait(operation, 'create')
#        operation = dm_write.WaitForOperation(
#            self.client,
#            self.messages,
#            operation.name,
#            project=self.config['project'],
#            timeout=self.OPERATION_TIMEOUT,
#            operation_description='create {} (fingerprint {})'.format(
#                self.config['name'],
#                fingerprint
#            )
#        )
        self.print_resources_and_outputs()


    def update(self, preview=False):
        """ Updates this deployment in DM

        Args:
            preview (boolean): If True, update is done with preview

        """

        # Get current deployment to figure out the fingerprint
        self.get()
        if not self.current:
            raise SystemExit(
                'Error updating {}: Deployment does not exist'.format(
                    self.config['name']
                )
            )

        print(self.current)

        new_deployment = self.messages.Deployment(
            name=self.config['name'],
            target=self.target_config,
            fingerprint=self.current.fingerprint or b''
        )

        request = self.messages.DeploymentmanagerDeploymentsUpdateRequest(
            deployment=self.config['name'],
            deploymentResource=new_deployment,
            project=self.config['project'],
            preview=preview or getattr(self.current, 'update', False)
#            createPolicy='CREATE_OR_ACQUIRE',
#            deletePolicy='DELETE'
        )
        LOG.debug(
            'Updating deployment %s with data %s',
            self.config['name'],
            request
        )

        # The actual update.
        # No exception handling is done here to allow higher level
        # functions to do so
        operation = self.client.deployments.Update(request)

        # Fetch and print the latest fingerprint of the deployment.
        self.get()

        # Wait for operation to finish
        self.wait(operation, 'update')

        self.print_resources_and_outputs()

        print(self.current)
        print(hasattr(self.current, 'update'))
        print(self.current.update)
        if preview:
            func = self.confirm_preview()
            func()
        elif getattr(self.current, 'update', False):
            self.update_preview()

    def confirm_preview(self):
        answer = ask()
        if answer == 'u':
            return self.update_preview
        elif answer == 's':
            return self.cancel_preview
        elif answer == 'a':
            raise SystemExit('Aborting deployment run!')
        else:
            ask()
#            raise SystemExit('Invalid answer: ' + answer)



    def update_preview(self):
        deployment = self.messages.Deployment(
            name=self.config['name'],
            fingerprint=self.current.fingerprint or b''
        )
        request = self.messages.DeploymentmanagerDeploymentsUpdateRequest(
            deployment=self.config['name'],
            deploymentResource=deployment,
            project=self.config['project'],
            preview=False
        )
        operation = self.client.deployments.Update(request)
        self.wait(operation, 'update preview')
        self.print_resources_and_outputs()


    def wait(self, operation, action):
        dm_write.WaitForOperation(
            self.client,
            self.messages,
            operation.name,
            project=self.config['project'],
            timeout=self.OPERATION_TIMEOUT,
            operation_description='{} {} (fingerprint {})'.format(
                action,
                self.config['name'],
                base64.urlsafe_b64encode(self.current.fingerprint)
            )
        )
        return self.get()

    def cancel_preview(self):
        cancel_msg = self.messages.DeploymentsCancelPreviewRequest(
            fingerprint=self.current.fingerprint or b''
        )
        req = self.messages.DeploymentmanagerDeploymentsCancelPreviewRequest(
            deployment=self.config['name'],
            deploymentsCancelPreviewRequest=cancel_msg,
            project=self.config['project']
        )
        operation = self.client.deployments.CancelPreview(req)
        self.wait(operation, 'cancel preview')

    def upsert(self, preview=False):
        """ Create or update this deployment in DM

        Args:
            preview (boolean): If True, update is done with preview

        """

        try:
            self.create()
        except apitools_exceptions.HttpConflictError as err:
            self.update(preview=preview)


    def print_resources_and_outputs(self):
        """ Print the Resources and Outputs of this deployment in DM """

        rsp = dm_api_util.FetchResourcesAndOutputs(
            self.client,
            self.messages,
            self.config['project'],
            self.config['name'],
#           self.ReleaseTrack() is base.ReleaseTrack.ALPHA
        )


        printer = resource_printer.Printer(flags.RESOURCES_AND_OUTPUTS_FORMAT)
        printer.AddRecord(rsp)
        printer.Finish()
        return rsp


#        dm_api_util.PrettyPrint(rsp.resources)
#        print('========== Resources ==========')
#        for r in rsp.resources:
#            print(r.__dict__)
##        print(yaml.dump(rsp.resources, indent=2))
#        print('========== Outputs ==========')
#        print(rsp.outputs)
##        print(yaml.dump(rsp.outputs, indent=2))
#
