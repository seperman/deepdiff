import pytest
from deepdiff import DeepDiff

t1 = {
    "foo": {
        "bar": {
            "veg": "potato",
            "fruit": "apple"
        }
    },
    "ingredients": [
        {
            "lunch": [
                "bread",
                "cheese"
            ]
        },
        {
            "dinner": [
                "soup",
                "meat"
            ]
        }
    ]
}
t2 = {
    "foo": {
        "bar": {
            "veg": "potato",
            "fruit": "peach"
        }
    },
    "ingredients": [
        {
            "lunch": [
                "bread",
                "cheese"
            ]
        },
        {
            "dinner": [
                "soup",
                "meat"
            ]
        }
    ]
}


class TestDeepDiffIncludePaths:

    @staticmethod
    def deep_diff(dict1, dict2, include_paths):
        diff = DeepDiff(dict1, dict2, include_paths=include_paths)
        print(diff)
        return diff

    def test_include_paths_root_neg(self):
        expected = {'values_changed': {"root['foo']['bar']['fruit']": {'new_value': 'peach', 'old_value': 'apple'}}}
        actual = self.deep_diff(t1, t2, 'foo')
        assert expected == actual

    def test_include_paths_root_pos(self):
        expected = {}
        actual = self.deep_diff(t1, t2, 'ingredients')
        assert expected == actual

    def test_include_paths_nest00_neg(self):
        expected = {'values_changed': {"root['foo']['bar']['fruit']": {'new_value': 'peach', 'old_value': 'apple'}}}
        actual = self.deep_diff(t1, t2, "root['foo']['bar']")
        assert expected == actual

    def test_include_paths_nest01_neg(self):
        expected = {'values_changed': {"root['foo']['bar']['fruit']": {'new_value': 'peach', 'old_value': 'apple'}}}
        actual = self.deep_diff(t1, t2, "root['foo']['bar']['fruit']")
        assert expected == actual

    def test_include_paths_nest_pos(self):
        expected = {}
        actual = self.deep_diff(t1, t2, "root['foo']['bar']['veg']")
        assert expected == actual

    @pytest.mark.parametrize(
        "test_num, data",
        [
            (
                1,  # test_num
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
                    "expected_result1": {'dictionary_item_added': ["root['new_attribute']"], 'values_changed': {"root['name']": {'new_value': 'Testname New', 'old_value': 'Testname Old'}, "root['desciption']": {'new_value': 'Desc New', 'old_value': 'Desc Old'}}},
                    "expected_result2": {},
                },
            ),
            (
                2,  # test_num
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
                    "expected_result1": {'dictionary_item_added': ["root['new_attribute']"], 'values_changed': {"root['name']": {'new_value': 'Testname New', 'old_value': 'Testname Old'}, "root['desciption']": {'new_value': 'Desc New', 'old_value': 'Desc Old'}, "root['sub_path']['name']": {'new_value': 'Testname Subpath New', 'old_value': 'Testname Subpath old'}}},
                    "expected_result2": {"values_changed": {"root['sub_path']['name']": {"old_value": "Testname Subpath old", "new_value": "Testname Subpath New"}}},
                },
            ),
            (
                3,  # test_num
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
                    "expected_result1": {'dictionary_item_added': ["root['new_attribute']", "root['sub_path']['new_sub_path_attr']"], 'dictionary_item_removed': ["root['sub_path']['old_attr']"], 'values_changed': {"root['name']": {'new_value': 'Testname New', 'old_value': 'Testname Old'}, "root['desciption']": {'new_value': 'Desc New', 'old_value': 'Desc Old'}, "root['sub_path']['desciption']": {'new_value': 'Desc Subpath New', 'old_value': 'Desc Subpath old'}}},
                    "expected_result2": {},
                },
            ),
            (
                4,  # test_num
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
                    "expected_result1": {'dictionary_item_added': ["root['sub_path']['added_attr']"], 'dictionary_item_removed': ["root['sub_path']['removed_attr']"], 'values_changed': {"root['name']": {'new_value': 'Testname new', 'old_value': 'Testname old'}, "root['desciption']": {'new_value': 'Desc new', 'old_value': 'Desc old'}, "root['new_attribute']": {'new_value': 'new Value', 'old_value': 'old Value'}}},
                    "expected_result2": {},
                },
            ),
            (
                5,  # test_num
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
                    "expected_result1": {'dictionary_item_added': ["root['added_attr']"], 'dictionary_item_removed': ["root['removed_attr']"]},
                    "expected_result2": {},
                },
            ),
            (
                6,  # test_num
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
                    "expected_result1": {'values_changed': {'root': {'new_value': {'added_attr': 'Added Attr Value', 'name': 'Testname'}, 'old_value': {'name': 'Testname', 'removed_attr': 'revemod attr value', 'removed_attr_2': 'revemod attr value'}}}},
                    "expected_result2": {},
                },
            ),
            (
                7,  # test_num
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
                    "expected_result1": {'values_changed': {"root['name']": {'new_value': 'Testname new', 'old_value': 'Testname old'}, "root['desciption']": {'new_value': 'Desc new', 'old_value': 'Desc old'}, "root['new_attribute']": {'new_value': 'new Value', 'old_value': 'old Value'}, "root['sub_path']": {'new_value': {'added_attr': 'Added Attr Value', 'name': 'Testname'}, 'old_value': {'name': 'Testname', 'removed_attr': 'revemod attr value', 'removed_attr_2': 'blu'}}}},
                    "expected_result2": {},
                },
            ),
            (
                8,  # test_num
                {
                    "old": [{
                        'name': 'Testname old',
                        'desciption': 'Desc old',
                        'new_attribute': 'old Value',
                        'sub_path': {
                            'name': 'Testname',
                            'removed_attr': 'revemod attr value',
                            'removed_attr_2': 'blu',
                        },
                    }],
                    "new": [{
                        'name': 'Testname new',
                        'desciption': 'Desc new',
                        'new_attribute': 'new Value',
                        'sub_path': {
                            'added_attr': 'Added Attr Value',
                            'name': 'New Testname',
                        },
                    }],
                    "include_paths": "root[0]['sub_path']['name']",
                    "expected_result1": {'values_changed': {"root[0]['name']": {'new_value': 'Testname new', 'old_value': 'Testname old'}, "root[0]['desciption']": {'new_value': 'Desc new', 'old_value': 'Desc old'}, "root[0]['new_attribute']": {'new_value': 'new Value', 'old_value': 'old Value'}, "root[0]['sub_path']": {'new_value': {'added_attr': 'Added Attr Value', 'name': 'New Testname'}, 'old_value': {'name': 'Testname', 'removed_attr': 'revemod attr value', 'removed_attr_2': 'blu'}}}},
                    "expected_result2": {'values_changed': {"root[0]['sub_path']['name']": {'new_value': 'New Testname', 'old_value': 'Testname'}}},
                },
            ),
        ]
    )
    def test_diff_include_paths_root(self, test_num, data):
        diff1 = DeepDiff(data["old"], data["new"])
        diff2 = DeepDiff(data["old"], data["new"], include_paths=data["include_paths"])
        assert data['expected_result1'] == diff1, f"test_diff_include_paths_root test_num #{test_num} failed."
        assert data['expected_result2'] == diff2, f"test_diff_include_paths_root test_num #{test_num} failed."
