from six import PY2

if PY2:
    import mock
else:
    import unittest.mock as mock

from cloud_foundation_toolkit import actions
from cloud_foundation_toolkit.deployment import Config, ConfigGraph


ACTIONS = ['apply', 'create', 'delete', 'update']


class Args(object):

    def __init__(self, **kwargs):
        self.preview = False
        [setattr(self, k, v) for k, v in kwargs.items()]


def get_number_of_elements(items):
    if isinstance(item, list):
        return sum(get_number_of_elements(subitem) for subitem in item)
    else:
        return 1


def test_execute(configs):
    args = Args(action='apply', config=[configs.directory], dry_run=False)
    with mock.patch('cloud_foundation_toolkit.actions.Deployment') as m1:
        graph = ConfigGraph([v.path for k, v in configs.files.items()])
        n_configs = len(configs.files)

        r = actions.execute(args)
        assert r == None
        assert m1.call_count == n_configs

        args.dry_run = True
        r = actions.execute(args)
        assert r == None
        assert m1.call_count == n_configs


def test_valid_actions():
    ACTUAL_ACTIONS = actions.ACTION_MAP.keys()
    ACTUAL_ACTIONS.sort()
    assert ACTUAL_ACTIONS == ACTIONS


def test_action(configs):
    args = Args(config=[configs.directory], dry_run=False)
    for action in ACTIONS:
        with mock.patch('cloud_foundation_toolkit.actions.Deployment') as m1:
            args.action = action
            r = actions.execute(args)
            n_configs = len(configs.files)
            method = getattr(mock.call(), action)
            assert m1.call_count == n_configs
            if action != 'delete':
                assert m1.mock_calls.count(method(preview=args.preview)) == n_configs
            else:
                assert m1.mock_calls.count(method()) == n_configs


def test_get_config_files(configs):
    r = actions.get_config_files([configs.directory])
    files = [v.path for k, v in configs.files.items()]
    files.sort()
    r.sort()
    assert files == r
