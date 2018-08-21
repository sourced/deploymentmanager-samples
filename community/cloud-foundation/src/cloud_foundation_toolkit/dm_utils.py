from collections import namedtuple
from six.moves.urllib.parse import urlparse
import yaml

from deployment import DM_API

API = DM_API()
DM_URL = namedtuple(
    'URL', ['project', 'deployment', 'name']
)


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
            '"dm://${project}/${deployment}/${name}"'
        )
    return DM_URL(parsed_url.netloc, *parsed_url.path.split('/')[1:])


def get_deployment_output(project, deployment, name):
    manifest = get_manifest(project, deployment)
    layout = yaml.load(manifest.layout)
    for resource in layout.get('resources', []):
        if resource['name'] != deployment:
            continue
        for output in resource.get('outputs', []):
            if output['name'] == name:
                return output['finalValue']
