import yaml

from dm_utils import get_deployment_output
from dm_utils import parse_dm_url


YAML_TAGS = [
    '!DMProperty',
    '!DMOutput',
]


def dmoutput_constructor(loader, node):
    """ Implements the !DMOutpuet yaml tag

    The tag takes string represeting an DM item URL.

    Example:
      network: !DMOutput dm://${project}/${deployment}/${name}

    """
    data = loader.construct_scalar(node)
    url = parse_dm_url(data)
    return get_deployment_output(url.project, url.deployment, url.name)


def yaml_constructor(loader, tag_suffix, node):
    """ Handles YAML tags used in this tool

    If the tag in not specific to this tool, the yaml Node() object is
    returned, so it can be rendered back into YAML by the *representer*
    function.
    """
    if tag_suffix in YAML_TAGS:
        function = globals()[
            '{}_constructor'.format(tag_suffix[1:]).lower()
        ]
        return function(loader, node)
    return node


def yaml_passthru_constructor(loader, tag_suffix, node):
    return node


def yaml_representer(dumper, data):
    return data


class DMYamlLoader(yaml.Loader):
    """ YAML loader class that handles custom tags

    This is the loader to be given as argument to yaml.load()
    When queries to DM are to be issued, normally during each
    deployment instatiation.

    Only tags in YAML_TAGS list at the top of this files are
    processed. Any other tags are left as is.
    """

    def __init__(self, *args, **kwargs):
        super(DMYamlLoader, self).__init__(*args, **kwargs)
        self.add_multi_constructor('', yaml_constructor)


# Default yaml loader/dumper ignores any tags (strings starting with !)
# This is used mostly on when parsing the main config, since at that
# point no deployments were executed, so deployment outputs and
# and properties cannot yet be queried
yaml.add_multi_constructor('', yaml_passthru_constructor)
yaml.add_multi_representer(yaml.nodes.Node, yaml_representer)
