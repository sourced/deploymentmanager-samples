from contextlib import nested
from six import PY2

if PY2:
    import mock
else:
    import unittest.mock as mock

from cloud_foundation_toolkit import actions
from cloud_foundation_toolkit.deployment import ConfigList

class Args(object):
    config = [['a1', 'b1', 'c1'], ['a21', 'a22', 'b21'], ['a31']]
    preview = False

def execute_action(action, args):
    with mock.patch('cloud_foundation_toolkit.actions.Deployment') as m1, \
         mock.patch('cloud_foundation_toolkit.actions.ConfigList') as m2:
        m2.return_value = [['x1', 'y1', 'z1'], ['x21', 'x22', 'y21'], ['z31']]
        f = getattr(actions, action)
        r = f(args)
    return (r, m1, m2)

def get_number_of_elements(item):
    if isinstance(item, list):
        return sum(get_number_of_elements(subitem) for subitem in item)
    else:
        return 1

def test_get():
    args = Args()
    r, m1, m2 = execute_action('get', args)
    # ensure action returned the correct value
    assert r == None
    # ensure the action was executed the correct number of times
    assert m1.call_count == get_number_of_elements(args.config)
    # ensure the right args were passed
    assert m1.mock_calls.count(mock.call().get()) == get_number_of_elements(args.config)

def test_create():
    args = Args()
    r, m1, m2 = execute_action('create', args)
    # ensure action returned the correct value
    assert r == None
    # ensure the action was executed the correct number of times
    assert m1.call_count == get_number_of_elements(args.config)
    # ensure the right args were passed
    assert m1.mock_calls.count(mock.call().create(preview=args.preview)) == get_number_of_elements(args.config)

def test_delete():
    args = Args()
    r, m1, m2 = execute_action('delete', args)
    # ensure action returned the correct value
    assert r == None
    # ensure the action was executed the correct number of times
    assert m1.call_count == get_number_of_elements(args.config)
    # ensure the right args were passed
    assert m1.mock_calls.count(mock.call().delete()) == get_number_of_elements(args.config)

def test_update():
    args = Args()
    r, m1, m2 = execute_action('update', args)
    # ensure action returned the correct value
    assert r == None
    # ensure the action was executed the correct number of times
    assert m1.call_count == get_number_of_elements(args.config)
    # ensure the right args were passed
    assert m1.mock_calls.count(mock.call().update(preview=args.preview)) == get_number_of_elements(args.config)

def test_apply():
    args = Args()
    r, m1, m2 = execute_action('apply', args)
    # ensure action returned the correct value
    assert r == None
    # ensure the action was executed the correct number of times
    assert m1.call_count == get_number_of_elements(args.config)
    # ensure the right args were passed
    assert m1.mock_calls.count(mock.call().apply(preview=args.preview)) == get_number_of_elements(args.config)
