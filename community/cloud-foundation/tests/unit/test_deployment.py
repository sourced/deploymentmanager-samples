from contextlib import nested
from six import PY2

from apitools.base.py.exceptions import HttpNotFoundError
import jinja2
import pytest

from cloud_foundation_toolkit.deployment import Config
from cloud_foundation_toolkit.deployment import ConfigList
from cloud_foundation_toolkit.deployment import Deployment

if PY2:
    import mock
else:
    import unittest.mock as mock

class Message():
    def __init__(self, **kwargs):
        [setattr(self, k, v) for k, v in kwargs.items()]


@pytest.fixture
def args():
    return Args()

def test_config(configs):
    c = Config(configs.files[0].path)
    assert c.raw == configs.files[0].content
    assert c.rendered == jinja2.Template(configs.files[0].content).render()


def test_config_list(configs):
    config_paths = [c.path for c in configs.files]
    config_list = ConfigList(config_paths)
    for level in config_list:
        assert isinstance(level, list)
        for c in level:
            assert isinstance(c, Config)


def test_deployment_object(configs):
    config = Config(configs.files[0].path)
    deployment = Deployment(config)
    assert deployment.config['name'] == 'my-network-prod'
    assert deployment.config['project'] == 'my-project'


def test_deployment_get(configs):
    config = Config(configs.files[0].path)
    deployment = Deployment(config)
    with mock.patch.object(deployment.client.deployments, 'Get') as m:
        m.return_value = Message(
            name='my-network-prod',
            fingerprint='abcdefgh'
        )
        d = deployment.get()
        assert d is not None
        assert deployment.current == d


def test_deployment_get_doesnt_exist(configs):
    config = Config(configs.files[0].path)
    deployment = Deployment(config)
    with mock.patch.object(deployment.client.deployments, 'Get') as m:
        m.side_effect = HttpNotFoundError('a', 'b', 'c')
        d = deployment.get()
        assert d is None
        assert deployment.current == d


def test_deployment_create(configs):
    config = Config(configs.files[0].path)
    patches = {
        'client': mock.DEFAULT,
        'wait': mock.DEFAULT,
        'get': mock.DEFAULT,
        'print_resources_and_outputs': mock.DEFAULT
    }

    with mock.patch.multiple(Deployment, **patches) as mocks:
        deployment = Deployment(config)
        mocks['client'].deployments.Insert.return_value = Message(
            name='my-network-prod',
            fingerprint='abcdefgh'
        )
        mocks['client'].deployments.Get.return_value = Message(
            name='my-network-prod',
            fingerprint='abcdefgh'
        )

        d = deployment.create()
        assert deployment.current == d

