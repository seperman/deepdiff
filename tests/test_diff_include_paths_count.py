import pytest
from deepdiff import DeepDiff

@pytest.mark.parametrize(
    "data, result",
    [
        (
            {
                "old": {
                    'name': 'Testname Old',
                    'desciption': 'Desc Old',
                    'sub_path': {
                        'name': 'Testname Subpath old',
                        'desciption': 'Desc Subpath old',
                    },
                },
                "new": {
                    'name': 'Testname New',
                    'desciption': 'Desc New',
                    'new_attribute': 'New Value',
                    'sub_path': {
                        'name': 'Testname Subpath old',
                        'desciption': 'Desc Subpath old',
                    },
                },
                "include_paths": "root['sub_path']",
            },
            {}
        ),
        (
            {
                "old": {
                    'name': 'Testname Old',
                    'desciption': 'Desc Old',
                    'sub_path': {
                        'name': 'Testname Subpath old',
                        'desciption': 'Desc Subpath old',
                    },
                },
                "new": {
                    'name': 'Testname New',
                    'desciption': 'Desc New',
                    'new_attribute': 'New Value',
                    'sub_path': {
                        'name': 'Testname Subpath New',
                        'desciption': 'Desc Subpath old',
                    },
                },
                "include_paths": "root['sub_path']",
            },
            {"values_changed": {"root['sub_path']['name']": {"old_value": "Testname Subpath old", "new_value": "Testname Subpath New"}}}
        ),
        (
            {
                "old": {
                    'name': 'Testname Old',
                    'desciption': 'Desc Old',
                    'sub_path': {
                        'name': 'Testname Subpath old',
                        'desciption': 'Desc Subpath old',
                        'old_attr': 'old attr value',
                    },
                },
                "new": {
                    'name': 'Testname New',
                    'desciption': 'Desc New',
                    'new_attribute': 'New Value',
                    'sub_path': {
                        'name': 'Testname Subpath old',
                        'desciption': 'Desc Subpath New',
                        'new_sub_path_attr': 'new sub path attr value',
                    },
                },
                "include_paths": "root['sub_path']['name']",
            },
            {}
        ),
        (
            {
                "old": {
                    'name': 'Testname old',
                    'desciption': 'Desc old',
                    'new_attribute': 'old Value',
                    'sub_path': {
                        'name': 'Testname',
                        'removed_attr': 'revemod attr value',
                    },
                },
                "new": {
                    'name': 'Testname new',
                    'desciption': 'Desc new',
                    'new_attribute': 'new Value',
                    'sub_path': {
                        'added_attr': 'Added Attr Value',
                        'name': 'Testname',
                    },
                },
                "include_paths": "root['sub_path']['name']",
            },
            {}
        ),
        (
            {
                "old": {
                    'name': 'Testname',
                    'removed_attr': 'revemod attr value',
                },
                "new": {
                    'added_attr': 'Added Attr Value',
                    'name': 'Testname',
                },
                "include_paths": "root['name']",
            },
            {}
        ),
        (
            {
                "old": {
                    'name': 'Testname',
                    'removed_attr': 'revemod attr value',
                    'removed_attr_2': 'revemod attr value',
                },
                "new": {
                    'added_attr': 'Added Attr Value',
                    'name': 'Testname',
                },
                "include_paths": "root['name']",
            },
            {}
        ),
        (
            {
                "old": {
                    'name': 'Testname old',
                    'desciption': 'Desc old',
                    'new_attribute': 'old Value',
                    'sub_path': {
                        'name': 'Testname',
                        'removed_attr': 'revemod attr value',
                        'removed_attr_2': 'blu',
                    },
                },
                "new": {
                    'name': 'Testname new',
                    'desciption': 'Desc new',
                    'new_attribute': 'new Value',
                    'sub_path': {
                        'added_attr': 'Added Attr Value',
                        'name': 'Testname',
                    },
                },
                "include_paths": "root['sub_path']['name']",
            },
            {}
        ),
    ]
)
def test_diff_include_paths_root(data, result):
    diff = DeepDiff(data["old"], data["new"], include_paths=data["include_paths"])
    assert diff == result
