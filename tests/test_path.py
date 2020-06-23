import pytest
from deepdiff.path import _path_to_elements, GET, GETATTR, extract


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
])
def test_get_item(obj, path, expected):
    result = extract(obj, path)
    assert expected == result
