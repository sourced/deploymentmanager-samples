from contextlib import nested
from six import PY2
#import unittest


if PY2:
    import mock
else:
    import unittest.mock as mock


#from unittest import MagicMock
#from unittest import patch

from cloud_foundation_toolkit import actions
from cloud_foundation_toolkit.deployment import ConfigList

#def create(args):
#    configs = ConfigList(args.config)
#    [Deployment(c).create(preview=args.preview) for c in configs]
#
#def delete(args):
#    configs = ConfigList(args.config)
#    [Deployment(c).delete() for c in configs[::-1]]
#

class Args(object):
    config = ['c1', 'c2', 'c3']
    preview = False

def execute_action(action, args):
#    with nested(
#            mock.patch('cloud_foundation_toolkit.actions.Deployment'),
#            mock.patch('cloud_foundation_toolkit.actions.ConfigList')
#        ) as (m1, m2):
    with mock.patch('cloud_foundation_toolkit.actions.Deployment') as m1, \
         mock.patch('cloud_foundation_toolkit.actions.ConfigList') as m2:
        m2.return_value = ['a', 'b', 'c']
        f = getattr(actions, action)
        r = f(args)
    return (r, m1, m2)

def test_create():
    args = Args()
    r, m1, m2 = execute_action('create', args)
    # ensure action returned the correct value
    assert r == None
    # ensure the action was executed the correct number of times
    assert m1.call_count == len(args.config)
    # ensure the right args were passed
    assert m1.mock_calls.count(mock.call().create(preview=args.preview)) == len(args.config)

def test_delete():
    args = Args()
    r, m1, m2 = execute_action('delete', args)
    # ensure action returned the correct value
    assert r == None
    # ensure the action was executed the correct number of times
    assert m1.call_count == len(args.config)

def test_update():
    args = Args()
    r, m1, m2 = execute_action('update', args)
    # ensure action returned the correct value
    assert r == None
    # ensure the action was executed the correct number of times
    assert m1.call_count == len(args.config)
    # ensure the right args were passed
    assert m1.mock_calls.count(mock.call().update(preview=args.preview)) == len(args.config)

#    with mock.patch('cloud_foundation_toolkit.actions.Deployment') as m1:
#        deployment = m1.return_value
#        deployment.delete.return_value = None
#        with mock.patch('cloud_foundation_toolkit.actions.ConfigList') as m2:
#            m2.return_value = ['a', 'b', 'c']
#            r = actions.create(args)
#            assert r == None
#        exc = yaml.constructor.ConstructorError(None, None, "random_exception")
#        mock_yaml.side_effect = exc
#
#        with pytest.raises(yaml.constructor.ConstructorError):
#            parse_jinja(stack_name, mako_template, parameters)
#

