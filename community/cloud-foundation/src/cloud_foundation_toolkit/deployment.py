import base64
import os
import tempfile
import yaml

import jinja2
from googlecloudsdk.api_lib.deployment_manager import dm_api_util
from googlecloudsdk.api_lib.deployment_manager import dm_base
from googlecloudsdk.api_lib.deployment_manager import exceptions as dm_exceptions
from googlecloudsdk.command_lib.deployment_manager import dm_util
from googlecloudsdk.command_lib.deployment_manager import dm_write
from googlecloudsdk.command_lib.deployment_manager.importer import BuildConfig
from googlecloudsdk.command_lib.deployment_manager.importer import BuildTargetConfig
from googlecloudsdk.third_party.apis.deploymentmanager.v2 import deploymentmanager_v2_messages as messages

from . import LOG

def run(path):
    config = Config(path)
    for d in config.deployments:
        LOG.debug('===> ' + d)
        Deployment(d).create()



class Config(object):
    """Class representing a config file """

    def __init__(self, path):
        """ Contructor

        Args:
            path (str): The path to the CFT config
        """

        # This is here to avoid circular imports
        import yaml_utils

        self.path = path

        with open(path) as f:
            self.raw = f.read()
        self.rendered = jinja2.Template(self.raw).render()
        self.obj = yaml.load(self.rendered)

    @property
    def deployments(self):
        """ Lazy-loads deployment objects for this config"""

        if not hasattr(self, '_deployments'):
            # single deployment in a config doesn't need to be in a list
            if isinstance(self.obj, dict):
                self._deployments = [yaml.dump(self.obj)]
            elif isinstance(self.obj, list):
                self._deployments = [yaml.dump(d) for d in self.obj]
            else:
                raise TypeError(
                    'Config must be a list or a dict representing a deployment'
            )
        return self._deployments

    def sort(self):
        """ Sorts the deployments based on the dependency graph"""

        pass


@dm_base.UseDmApi(dm_base.DmApiVersion.V2)
class DM_API(dm_base.DmCommand):
    """ Class representing the DM API

    This a proxy class only, so other modules in this project
    only import this local class instead of gcloud's. Here's the source:

    https://github.com/google-cloud-sdk/google-cloud-sdk/blob/master/lib/googlecloudsdk/api_lib/deployment_manager/dm_base.py
    """


class Deployment(DM_API):
    """ Class representing a deployment """

    # Number of seconds to wait for a create/update/delete operation
    OPERATION_TIMEOUT = 20 * 60 # 20 mins. Same as gcloud

    # The keys required by a DM config (not CFT config)
    DM_CONFIG_KEYS = ['imports', 'resources', 'outputs']

    def __init__(self, config):
        """ The class constructor

        Args:
            config (dict): A dict representing CFT config. Normally
                provided when creating/updating a deployment.
        """

        # Use custom yaml tags only during deployment instantiation
        # because if done before, the DM queries implemented for the
        # tags would fail with 404s
        import yaml_utils
        config = yaml.load(config, Loader=yaml_utils.DMYamlLoader)

        config['project'] = config.get('project', dm_base.GetProject())
        self.config = config
        LOG.debug('==> '+ str(self.config))
        self.fingerprint = None

    def render(self, content=None):
        """ Returns a yaml dump of the deployment"""
        #content = content or self.__dict__
        content = content or self.dm_config
        return yaml.dump(content, indent=2)


    def write_file(self):
        """ Writes the yaml dump of the deployment to a temp file"""

        with tempfile.NamedTemporaryFile(dir=os.getcwd(), delete=False) as tmp:
            tmp.write(self.render())
            self.path = tmp.name

    def delete_file(self):
        os.remove(self.path)

    @property
    def dm_config(self):
        return {
            k: v for k, v in self.config.items() if k in self.DM_CONFIG_KEYS
        }

    @property
    def target_config(self):
        self.write_file()
        target = BuildTargetConfig(messages, config=self.path)
        self.delete_file()
        return target

    def create(self):
        depl = self.messages.Deployment(
            name=self.config['name'],
            target=self.target_config
        )
        request = self.messages.DeploymentmanagerDeploymentsInsertRequest(
            deployment=depl,
            project=self.config['project'],
#            createPolicy='CREATE_OR_ACQUIRE'
        )
        LOG.debug(
            'Creating deployment {} with data {}'.format(
                self.config['name'],
                request
            )
        )

        operation = self.client.deployments.Insert(request)


        # Fetch and print the latest fingerprint of the deployment.
        fingerprint = dm_api_util.FetchDeploymentFingerprint(
            self.client,
            self.messages,
            self.config['project'],
            self.config['name']
        )
        self.fingerprint = base64.urlsafe_b64encode(fingerprint)

        operation = dm_write.WaitForOperation(
            self.client,
            self.messages,
            operation.name,
            project=self.config['project'],
            timeout=self.OPERATION_TIMEOUT,
            operation_description='create {}, fingerprint {}'.format(
                self.config['name'],
                self.fingerprint
            )
        )
