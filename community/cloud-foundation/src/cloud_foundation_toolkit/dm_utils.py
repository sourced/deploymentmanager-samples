from collections import namedtuple
from six.moves.urllib.parse import urlparse
import yaml

from googlecloudsdk.api_lib.deployment_manager import dm_base
#from deployment import DM_API

DM_URL = namedtuple(
    'URL', ['project', 'deployment', 'resource', 'name']
)


@dm_base.UseDmApi(dm_base.DmApiVersion.V2)
class DM_API(dm_base.DmCommand):
    """ Class representing the DM API

    This a proxy class only, so other modules in this project
    only import this local class instead of gcloud's. Here's the source:

    https://github.com/google-cloud-sdk/google-cloud-sdk/blob/master/lib/googlecloudsdk/api_lib/deployment_manager/dm_base.py
    """
API = DM_API()


def get_deployment(project, deployment):
    return API.client.deployments.Get(
        API.messages.DeploymentmanagerDeploymentsGetRequest(
            project=project,
            deployment=deployment
        )
    )


def get_manifest(project, deployment):
    deployment_rsp = get_deployment(project, deployment)

    return API.client.manifests.Get(
        API.messages.DeploymentmanagerManifestsGetRequest(
            project=project,
            deployment=deployment,
            manifest=deployment_rsp.manifest.split('/')[-1]
        )
    )


def parse_dm_url(url):
    parsed_url = urlparse(url)
    if parsed_url.scheme != 'dm':
        raise ValueError(
            'The url must look like '
            '"dm://${project}/${deployment}/${resource}/${name}"'
        )
    return DM_URL(parsed_url.netloc, *parsed_url.path.split('/')[1:])


def get_deployment_output(project, deployment, resource, name):
    manifest = get_manifest(project, deployment)
    layout = yaml.load(manifest.layout)
    for r in layout.get('resources', []):
        if r['name'] != resource:
            continue
        for output in r.get('outputs', []):
            if output['name'] == name:
                return output['finalValue']
