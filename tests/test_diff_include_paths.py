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
