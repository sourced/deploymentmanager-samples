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


#def run(paths):
#    config = Config(paths)
#    for i in config:
#        LOG.debug('===> %s', i.rendered)
#        deployment = Deployment(i)
#        try:
#            deployment.create()
#        except apitools_exceptions.HttpConflictError as err:
#            deployment.update()
#

def ask():
    answer = input("Update(u), Skip (s), or Abort(a) Deployment? ")
    while answer not in ['u', 's', 'a']:
        answer = input("Update(u), Skip (s), or Abort(a) Deployment? ")
    return answer



class Config(object):
    """ Class representing a CFT config
    """

    def __init__(self, item):
        """ Contructor

        Args:
            item (str): The content or the path to a config file
        """

        if os.path.exists(item):
            with open(item) as f:
                self.raw = f.read()
        else:
            self.raw = item

        self.rendered = jinja2.Template(self.raw).render()


class ConfigList(list):
    """ A container Class for CFT config files

    This class holds ConfigFile() objects. For all intents and purposes
    it's a list().

    """

#    def __init__(self, paths):
    def __init__(self, items):
        """ Contructor

        Args:
            paths (str): The paths to the CFT configs.
                paths can be a list of files, a directory, or wildcards
                such as "*", or "/some/dir/prod*". In the case of
                wildcards, only files with extentions ".yaml", ".yml"
                and ".jinja" are matched

        """

        super(ConfigList, self).__init__([Config(item) for item in items])
#        self._items = [ConfigFile(path) for path in paths]
        self.sort()

#    def __iter__(self):
#        """ This makes the class behave like a list """
#        return iter(self._items)


#    def __getitem__(self, key):
#        return self._items[key]


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

    def delete(self, delete_policy=None):
        """Deletes this deployment from DM."""

        message = self.messages.DeploymentmanagerDeploymentsDeleteRequest
        request = message(
            deployment=self.config['name'],
            project=self.config['project']
        )

        if delete_policy:
            request['deletePolicy'] = message.DeletePolicyValueValuesEnum(
                delete_policy
            )

        LOG.debug(
            'Deleting deployment %',
            self.config['name'],
            request
        )
        operation = self.client.deployments.Delete(request)

        # Wait for operation to finish
        self.wait(operation, 'delete')

    def create(self, preview=False, create_policy=None):
        """Creates this deployment in DM."""

        deployment = self.messages.Deployment(
            name=self.config['name'],
            target=self.target_config
        )

        message = self.messages.DeploymentmanagerDeploymentsInsertRequest
        request = message(
            deployment=deployment,
            project=self.config['project'],
            preview=preview
        )
        if create_policy:
            request['createPolicy'] = message.CreatePolicyValueValuesEnum(
                create_policy
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
#
#        if preview:
#            func = self.confirm_preview()
#            func()
#        elif getattr(self.current, 'update', False):
#            self.update_preview()
#

    def update(self, preview=False, create_policy=None, delete_policy=None):
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

        new_deployment = self.messages.Deployment(
            name=self.config['name'],
            target=self.target_config,
            fingerprint=self.current.fingerprint or b''
        )

        message = self.messages.DeploymentmanagerDeploymentsUpdateRequest
        request = message(
            deployment=self.config['name'],
            deploymentResource=new_deployment,
            project=self.config['project'],
            preview=preview or getattr(self.current, 'update', False)
#            createPolicy='CREATE_OR_ACQUIRE',
#            deletePolicy='DELETE'
        )
        if delete_policy:
            request['deletePolicy'] = message.DeletePolicyValueValuesEnum(
                delete_policy
            )
        if create_policy:
            request['createPolicy'] = message.CreatePolicyValueValuesEnum(
                create_policy
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

        # Wait for operation to finish
        self.wait(operation, 'update')

        self.print_resources_and_outputs()

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
            raise SystemExit('Not a valid answer: {}'.format(answer))


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


    def wait(self, operation, action, get=True):
        """
        """
        # This saves an API call if the self.get() was called just
        # before calling this method
        if get:
            self.get()

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

    def sync(self, preview=False):
        """Create or update this deployment in DM.

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
