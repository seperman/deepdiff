import pytest
from deepdiff.path import _path_to_elements, GET, GETATTR, extract, parse_path


@pytest.mark.parametrize('path, expected', [
    ("root[4]['b'][3]", [(4, GET), ('b', GET), (3, GET)]),
    ("root[4].b[3]", [(4, GET), ('b', GETATTR), (3, GET)]),
    ("root[4].b['a3']", [(4, GET), ('b', GETATTR), ('a3', GET)]),
    ("root[4.3].b['a3']", [(4.3, GET), ('b', GETATTR), ('a3', GET)]),
    ("root.a.b", [('a', GETATTR), ('b', GETATTR)]),
    ("root.hello", [('hello', GETATTR)]),
    (r"root['a\rb']", [('a\rb', GET)]),
    ("root", []),
    (((4, GET), ('b', GET)), ((4, GET), ('b', GET))),
])
def test_path_to_elements(path, expected):
    result = _path_to_elements(path, root_element=None)
    assert tuple(expected) == result


@pytest.mark.parametrize('obj, path, expected', [
    ({1: [2, 3], 2: [4, 5]},
     "root[2][1]",
     5),
    ({1: [{'2': 'b'}, 3], 2: {4, 5}},
     "root[1][0]['2']",
     'b'),
    ({'test [a]': 'b'},
     "root['test [a]']",
     'b'),
])
def test_get_item(obj, path, expected):
    result = extract(obj, path)
    assert expected == result


def test_parse_path():
    result = parse_path("root[1][2]['age']")
    assert [1, 2, 'age'] == result
    result2 = parse_path("root[1][2]['age']", include_actions=True)
    assert [{'element': 1, 'action': 'GET'}, {'element': 2, 'action': 'GET'}, {'element': 'age', 'action': 'GET'}] == result2
    result3 = parse_path("root['joe'].age")
    assert ['joe', 'age'] == result3
    result4 = parse_path("root['joe'].age", include_actions=True)
    assert [{'element': 'joe', 'action': 'GET'}, {'element': 'age', 'action': 'GETATTR'}] == result4
