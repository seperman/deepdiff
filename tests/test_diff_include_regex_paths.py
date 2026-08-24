import re
from deepdiff import DeepDiff


class TestDeepDiffIncludeRegexPaths:

    def test_include_regex_paths_single_string(self):
        t1 = [{'a': 1, 'b': 2}, {'c': 4, 'b': 5}]
        t2 = [{'a': 9, 'b': 3}, {'c': 4, 'b': 8}]
        ddiff = DeepDiff(t1, t2, include_regex_paths=r"root\[\d+\]\['b'\]")
        expected = {'values_changed': {
            "root[0]['b']": {'new_value': 3, 'old_value': 2},
            "root[1]['b']": {'new_value': 8, 'old_value': 5},
        }}
        assert expected == ddiff

    def test_include_regex_paths_list(self):
        t1 = {"a": 1, "b": 2, "c": 3}
        t2 = {"a": 10, "b": 20, "c": 30}
        ddiff = DeepDiff(t1, t2, include_regex_paths=[r"\['a'\]", r"\['c'\]"])
        expected = {'values_changed': {
            "root['a']": {'new_value': 10, 'old_value': 1},
            "root['c']": {'new_value': 30, 'old_value': 3},
        }}
        assert expected == ddiff

    def test_include_regex_paths_compiled(self):
        t1 = [{'a': 1, 'b': 2}, {'c': 4, 'b': 5}]
        t2 = [{'a': 9, 'b': 3}, {'c': 4, 'b': 8}]
        pattern = re.compile(r"\['a'\]")
        ddiff = DeepDiff(t1, t2, include_regex_paths=[pattern])
        expected = {'values_changed': {"root[0]['a']": {'new_value': 9, 'old_value': 1}}}
        assert expected == ddiff

    def test_include_regex_paths_ancestor_keeps_subtree(self):
        # Anchoring to a parent path should keep the whole subtree, the same way
        # exclude_regex_paths on a parent drops the whole subtree.
        t1 = {"foo": {"bar": "potato", "veg": "x"}, "other": {"z": 1}}
        t2 = {"foo": {"bar": "banana", "veg": "y"}, "other": {"z": 2}}
        ddiff = DeepDiff(t1, t2, include_regex_paths=r"root\['foo'\]$")
        expected = {'values_changed': {
            "root['foo']['bar']": {'new_value': 'banana', 'old_value': 'potato'},
            "root['foo']['veg']": {'new_value': 'y', 'old_value': 'x'},
        }}
        assert expected == ddiff

    def test_include_regex_paths_no_match(self):
        t1 = {"a": 1, "b": 2}
        t2 = {"a": 10, "b": 20}
        ddiff = DeepDiff(t1, t2, include_regex_paths=r"\['does_not_exist'\]")
        assert {} == ddiff

    def test_include_regex_paths_added_and_removed(self):
        t1 = {"keep": {"x": 1}, "drop": {"y": 1}}
        t2 = {"keep": {"x": 1, "new": 9}, "drop": {}}
        ddiff = DeepDiff(t1, t2, include_regex_paths=r"root\['keep'\]")
        expected = {'dictionary_item_added': ["root['keep']['new']"]}
        assert expected == ddiff

    def test_include_regex_paths_default_unchanged(self):
        t1 = {"a": 1, "b": 2}
        t2 = {"a": 10, "b": 20}
        assert DeepDiff(t1, t2) == DeepDiff(t1, t2, include_regex_paths=None)

    def test_include_regex_paths_with_ignore_order(self):
        t1 = {"nums": [1, 2, 3], "letters": ["a", "b"]}
        t2 = {"nums": [3, 2, 1], "letters": ["a", "c"]}
        ddiff = DeepDiff(t1, t2, include_regex_paths=r"root\['letters'\]", ignore_order=True)
        expected = {'values_changed': {
            "root['letters'][1]": {'new_value': 'c', 'old_value': 'b'},
        }}
        assert expected == ddiff
