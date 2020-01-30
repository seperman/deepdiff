#!/usr/bin/env python
import datetime
import pytest
import logging
from unittest import mock
from decimal import Decimal
from deepdiff import DeepDiff
from deepdiff.helper import number_to_string
from deepdiff.helper import pypy3
from tests import CustomClass, CustomClass2

logging.disable(logging.CRITICAL)


class TestDeepDiffText:
    """DeepDiff Tests."""

    def test_same_objects(self):
        t1 = {1: 1, 2: 2, 3: 3}
        t2 = t1
        assert {} == DeepDiff(t1, t2)

    def test_item_type_change(self):
        t1 = {1: 1, 2: 2, 3: 3}
        t2 = {1: 1, 2: "2", 3: 3}
        ddiff = DeepDiff(t1, t2)
        assert {
            'type_changes': {
                "root[2]": {
                    "old_value": 2,
                    "old_type": int,
                    "new_value": "2",
                    "new_type": str
                }
            }
        } == ddiff

    def test_item_type_change_less_verbose(self):
        t1 = {1: 1, 2: 2, 3: 3}
        t2 = {1: 1, 2: "2", 3: 3}
        assert {'type_changes': {
                "root[2]": {
                    "old_type": int,
                    "new_type": str
                }
                }} == DeepDiff(t1, t2, verbose_level=0)

    def test_item_type_change_for_strings_ignored_by_default(self):
        """ ignore_string_type_changes = True by default """

        t1 = 'hello'
        t2 = b'hello'
        ddiff = DeepDiff(t1, t2, ignore_string_type_changes=True)
        assert not ddiff

    def test_item_type_change_for_strings_override(self):
        t1 = 'hello'
        t2 = b'hello'
        ddiff = DeepDiff(t1, t2, ignore_string_type_changes=False)
        assert {
            'type_changes': {
                'root': {
                    'old_type': str,
                    'new_type': bytes,
                    'old_value': 'hello',
                    'new_value': b'hello'
                }
            }
        } == ddiff

    @pytest.mark.parametrize("t1, t2, significant_digits, ignore_order, result", [
        (10, 10.0, 5, False, {}),
        ({10: 'a', 11.1: 'b'}, {10.0: 'a', Decimal('11.1000003'): 'b'}, 5, False, {}),
    ])
    def test_type_change_numeric_ignored(self, t1, t2, significant_digits, ignore_order, result):
        ddiff = DeepDiff(t1, t2, ignore_numeric_type_changes=True,
                         significant_digits=significant_digits, ignore_order=ignore_order)
        assert result == ddiff

    @pytest.mark.parametrize("t1, t2, expected_result",
                             [
                                 (10, 10.0, {}),
                                 (10, 10.2, {'values_changed': {'root': {'new_value': 10.2, 'old_value': 10}}}),
                                 (Decimal(10), 10.0, {}),
                                 ({"a": Decimal(10), "b": 12, 11.0: None}, {b"b": 12, "a": 10.0, Decimal(11): None}, {}),
                             ])
    def test_type_change_numeric_when_ignore_order(self, t1, t2, expected_result):
        ddiff = DeepDiff(t1, t2, ignore_order=True, ignore_numeric_type_changes=True, ignore_string_type_changes=True)
        assert expected_result == ddiff

    def test_value_change(self):
        t1 = {1: 1, 2: 2, 3: 3}
        t2 = {1: 1, 2: 4, 3: 3}
        result = {
            'values_changed': {
                'root[2]': {
                    "old_value": 2,
                    "new_value": 4
                }
            }
        }
        assert result == DeepDiff(t1, t2)

    def test_item_added_and_removed(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: 4}
        t2 = {1: 1, 2: 4, 3: 3, 5: 5, 6: 6}
        ddiff = DeepDiff(t1, t2)
        result = {
            'dictionary_item_added': {'root[5]', 'root[6]'},
            'dictionary_item_removed': {'root[4]'},
            'values_changed': {
                'root[2]': {
                    "old_value": 2,
                    "new_value": 4
                }
            }
        }
        assert result == ddiff

    def test_item_added_and_removed_verbose(self):
        t1 = {1: 1, 3: 3, 4: 4}
        t2 = {1: 1, 3: 3, 5: 5, 6: 6}
        ddiff = DeepDiff(t1, t2, verbose_level=2)
        result = {
            'dictionary_item_removed': {
                'root[4]': 4
            },
            'dictionary_item_added': {
                'root[6]': 6,
                'root[5]': 5
            }
        }
        assert result == ddiff

    def test_diffs_dates(self):
        t1 = datetime.date(2016, 8, 8)
        t2 = datetime.date(2016, 8, 7)
        ddiff = DeepDiff(t1, t2)
        result = {
            'values_changed': {
                'root': {
                    'new_value': t2,
                    'old_value': t1
                }
            }
        }
        assert result == ddiff

    def test_diffs_timedeltas(self):
        t1 = datetime.timedelta(days=1, seconds=12)
        t2 = datetime.timedelta(days=1, seconds=10)
        t3 = datetime.timedelta(seconds=(60*60*24) + 12)
        ddiff = DeepDiff(t1, t2)
        result = {
            'values_changed': {
                'root': {
                    'new_value': t2,
                    'old_value': t1
                }
            }
        }
        assert result == ddiff
        ddiff = DeepDiff(t1, t3)
        result = {}
        assert result == ddiff

    def test_string_difference(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world"}}
        t2 = {1: 1, 2: 4, 3: 3, 4: {"a": "hello", "b": "world!"}}
        ddiff = DeepDiff(t1, t2)
        result = {
            'values_changed': {
                'root[2]': {
                    'old_value': 2,
                    'new_value': 4
                },
                "root[4]['b']": {
                    'old_value': 'world',
                    'new_value': 'world!'
                }
            }
        }
        assert result == ddiff

    def test_diffs_equal_strings_when_not_identical(self):
        t1 = 'hello'
        t2 = 'hel'
        t2 += 'lo'
        assert t1 is not t2
        ddiff = DeepDiff(t1, t2)
        assert {} == ddiff

    def test_string_difference2(self):
        t1 = {
            1: 1,
            2: 2,
            3: 3,
            4: {
                "a": "hello",
                "b": "world!\nGoodbye!\n1\n2\nEnd"
            }
        }
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world\n1\n2\nEnd"}}
        ddiff = DeepDiff(t1, t2)
        result = {
            'values_changed': {
                "root[4]['b']": {
                    'diff':
                    '--- \n+++ \n@@ -1,5 +1,4 @@\n-world!\n-Goodbye!\n+world\n 1\n 2\n End',
                    'new_value': 'world\n1\n2\nEnd',
                    'old_value': 'world!\nGoodbye!\n1\n2\nEnd'
                }
            }
        }
        assert result == ddiff

    def test_string_difference_ignore_case(self):
        t1 = "Hello"
        t2 = "hello"

        ddiff = DeepDiff(t1, t2)
        result = {'values_changed': {'root': {'new_value': 'hello', 'old_value': 'Hello'}}}
        assert result == ddiff

        ddiff = DeepDiff(t1, t2, ignore_string_case=True)
        result = {}
        assert result == ddiff

    def test_bytes(self):
        t1 = {
            1: 1,
            2: 2,
            3: 3,
            4: {
                "a": b"hello",
                "b": b"world!\nGoodbye!\n1\n2\nEnd",
                "c": b"\x80",
            }
        }
        t2 = {1: 1,
              2: 2,
              3: 3,
              4: {
                  "a": b"hello",
                  "b": b"world\n1\n2\nEnd",
                  "c": b'\x81',
              }
        }

        ddiff = DeepDiff(t1, t2)
        result = {
            'values_changed': {
                "root[4]['b']": {
                    'diff':
                    '--- \n+++ \n@@ -1,5 +1,4 @@\n-world!\n-Goodbye!\n+world\n 1\n 2\n End',
                    'new_value': b'world\n1\n2\nEnd',
                    'old_value': b'world!\nGoodbye!\n1\n2\nEnd'
                },
                "root[4]['c']": {
                    'new_value': b'\x81',
                    'old_value': b'\x80'
                }
            }
        }
        assert result == ddiff

    def test_unicode(self):
        t1 = {
            1: 1,
            2: 2,
            3: 3,
            4: {
                "a": "hello",
                "b": "world!\nGoodbye!\n1\n2\nEnd"
            }
        }
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world\n1\n2\nEnd"}}
        ddiff = DeepDiff(t1, t2)
        result = {
            'values_changed': {
                "root[4]['b']": {
                    'diff':
                    '--- \n+++ \n@@ -1,5 +1,4 @@\n-world!\n-Goodbye!\n+world\n 1\n 2\n End',
                    'new_value': 'world\n1\n2\nEnd',
                    'old_value': 'world!\nGoodbye!\n1\n2\nEnd'
                }
            }
        }
        assert result == ddiff

    def test_type_change(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3]}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world\n\n\nEnd"}}
        ddiff = DeepDiff(t1, t2)
        result = {
            'type_changes': {
                "root[4]['b']": {
                    'old_type': list,
                    'new_value': 'world\n\n\nEnd',
                    'old_value': [1, 2, 3],
                    'new_type': str
                }
            }
        }
        assert result == ddiff

    def test_list_difference(self):
        t1 = {
            1: 1,
            2: 2,
            3: 3,
            4: {
                "a": "hello",
                "b": [1, 2, 'to_be_removed', 'to_be_removed2']
            }
        }
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2]}}
        ddiff = DeepDiff(t1, t2)
        result = {
            'iterable_item_removed': {
                "root[4]['b'][2]": "to_be_removed",
                "root[4]['b'][3]": 'to_be_removed2'
            }
        }
        assert result == ddiff

    def test_list_difference_add(self):
        t1 = [1, 2]
        t2 = [1, 2, 3, 5]
        ddiff = DeepDiff(t1, t2)
        result = {'iterable_item_added': {'root[2]': 3, 'root[3]': 5}}
        assert result == ddiff

    def test_list_difference2(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3, 10, 12]}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 3, 2]}}
        result = {
            'values_changed': {
                "root[4]['b'][2]": {
                    'new_value': 2,
                    'old_value': 3
                },
                "root[4]['b'][1]": {
                    'new_value': 3,
                    'old_value': 2
                }
            },
            'iterable_item_removed': {
                "root[4]['b'][3]": 10,
                "root[4]['b'][4]": 12
            }
        }
        ddiff = DeepDiff(t1, t2)
        assert result == ddiff

    def test_list_difference3(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 5]}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 3, 2, 5]}}
        ddiff = DeepDiff(t1, t2)
        result = {
            'values_changed': {
                "root[4]['b'][2]": {
                    'new_value': 2,
                    'old_value': 5
                },
                "root[4]['b'][1]": {
                    'new_value': 3,
                    'old_value': 2
                }
            },
            'iterable_item_added': {
                "root[4]['b'][3]": 5
            }
        }
        assert result == ddiff

    def test_list_difference4(self):
        # TODO: Look into Levenshtein algorithm
        # So that the result is just insertion of "c" in this test.
        t1 = ["a", "b", "d", "e"]
        t2 = ["a", "b", "c", "d", "e"]
        ddiff = DeepDiff(t1, t2)
        result = {
            'values_changed': {
                'root[2]': {
                    'new_value': 'c',
                    'old_value': 'd'
                },
                'root[3]': {
                    'new_value': 'd',
                    'old_value': 'e'
                }
            },
            'iterable_item_added': {
                'root[4]': 'e'
            }
        }
        assert result == ddiff

    def test_list_difference_ignore_order(self):
        t1 = {1: 1, 4: {"a": "hello", "b": [1, 2, 3]}}
        t2 = {1: 1, 4: {"a": "hello", "b": [1, 3, 2, 3]}}
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        assert {} == ddiff

    @pytest.mark.parametrize('t1_0, t2_0', [
        (1, 2),
        (True, False),
        ('a', 'b'),
    ])
    def test_list_difference_of_bool_only_ignore_order(self, t1_0, t2_0):
        t1 = [t1_0]
        t2 = [t2_0]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        result = {'iterable_item_added': {'root[0]': t2_0}, 'iterable_item_removed': {'root[0]': t1_0}}
        assert result == ddiff

    def test_dictionary_difference_ignore_order(self):
        t1 = {"a": [[{"b": 2, "c": 4}, {"b": 2, "c": 3}]]}
        t2 = {"a": [[{"b": 2, "c": 3}, {"b": 2, "c": 4}]]}
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        assert {} == ddiff

    def test_nested_list_ignore_order(self):
        t1 = [1, 2, [3, 4]]
        t2 = [[4, 3, 3], 2, 1]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        assert {} == ddiff

    def test_nested_list_difference_ignore_order(self):
        t1 = [1, 2, [3, 4]]
        t2 = [[4, 3], 2, 1]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        assert {} == ddiff

    def test_nested_list_with_dictionarry_difference_ignore_order(self):
        t1 = [1, 2, [3, 4, {1: 2}]]
        t2 = [[4, 3, {1: 2}], 2, 1]

        ddiff = DeepDiff(t1, t2, ignore_order=True)

        result = {}
        assert result == ddiff

    def test_list_difference_ignore_order_report_repetition(self):
        t1 = [1, 3, 1, 4]
        t2 = [4, 4, 1]
        ddiff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True)
        result = {
            'iterable_item_removed': {
                'root[1]': 3
            },
            'repetition_change': {
                'root[0]': {
                    'old_repeat': 2,
                    'old_indexes': [0, 2],
                    'new_indexes': [2],
                    'value': 1,
                    'new_repeat': 1
                },
                'root[3]': {
                    'old_repeat': 1,
                    'old_indexes': [3],
                    'new_indexes': [0, 1],
                    'value': 4,
                    'new_repeat': 2
                }
            }
        }
        assert result == ddiff

    # TODO: fix repeition report
    def test_nested_list_ignore_order_report_repetition_wrong_currently(self):
        t1 = [1, 2, [3, 4]]
        t2 = [[4, 3, 3], 2, 1]
        ddiff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True)
        result = {
            'repetition_change': {
                'root[2][0]': {
                    'old_repeat': 1,
                    'new_indexes': [1, 2],
                    'old_indexes': [1],
                    'value': 3,
                    'new_repeat': 2
                }
            }
        }
        assert result != ddiff

    def test_list_of_unhashable_difference_ignore_order(self):
        t1 = [{"a": 2}, {"b": [3, 4, {1: 1}]}]
        t2 = [{"b": [3, 4, {1: 1}]}, {"a": 2}]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        assert {} == ddiff

    def test_list_of_unhashable_difference_ignore_order2(self):
        t1 = [1, {"a": 2}, {"b": [3, 4, {1: 1}]}, "B"]
        t2 = [{"b": [3, 4, {1: 1}]}, {"a": 2}, {1: 1}]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        result = {
            'iterable_item_added': {
                'root[2]': {
                    1: 1
                }
            },
            'iterable_item_removed': {
                'root[3]': 'B',
                'root[0]': 1
            }
        }
        assert result == ddiff

    def test_list_of_unhashable_difference_ignore_order3(self):
        t1 = [1, {"a": 2}, {"a": 2}, {"b": [3, 4, {1: 1}]}, "B"]
        t2 = [{"b": [3, 4, {1: 1}]}, {1: 1}]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        result = {
            'iterable_item_added': {
                'root[1]': {
                    1: 1
                }
            },
            'iterable_item_removed': {
                'root[4]': 'B',
                'root[0]': 1,
                'root[1]': {
                    'a': 2
                }
            }
        }
        assert result == ddiff

    def test_list_of_unhashable_difference_ignore_order_report_repetition(
            self):
        t1 = [1, {"a": 2}, {"a": 2}, {"b": [3, 4, {1: 1}]}, "B"]
        t2 = [{"b": [3, 4, {1: 1}]}, {1: 1}]
        ddiff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True)
        result = {
            'iterable_item_added': {
                'root[1]': {
                    1: 1
                }
            },
            'iterable_item_removed': {
                'root[4]': 'B',
                'root[0]': 1,
                'root[1]': {
                    'a': 2
                },
                'root[2]': {
                    'a': 2
                }
            }
        }
        assert result == ddiff

    def test_list_of_unhashable_difference_ignore_order4(self):
        t1 = [{"a": 2}, {"a": 2}]
        t2 = [{"a": 2}]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        result = {}
        assert result == ddiff

    def test_list_of_unhashable_difference_ignore_order_report_repetition2(
            self):
        t1 = [{"a": 2}, {"a": 2}]
        t2 = [{"a": 2}]
        ddiff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True)
        result = {
            'repetition_change': {
                'root[0]': {
                    'old_repeat': 2,
                    'new_indexes': [0],
                    'old_indexes': [0, 1],
                    'value': {
                        'a': 2
                    },
                    'new_repeat': 1
                }
            }
        }
        assert result == ddiff

    def test_list_of_sets_difference_ignore_order(self):
        t1 = [{1}, {2}, {3}]
        t2 = [{4}, {1}, {2}, {3}]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        result = {'iterable_item_added': {'root[0]': {4}}}
        assert result == ddiff

    def test_list_of_sets_difference_ignore_order_when_there_is_duplicate(
            self):
        t1 = [{1}, {2}, {3}]
        t2 = [{4}, {1}, {2}, {3}, {3}]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        result = {'iterable_item_added': {'root[0]': {4}}}
        assert result == ddiff

    def test_list_of_sets_difference_ignore_order_when_there_is_duplicate_and_mix_of_hashable_unhashable(
            self):
        t1 = [1, 1, {2}, {3}]
        t2 = [{4}, 1, {2}, {3}, {3}, 1, 1]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        result = {'iterable_item_added': {'root[0]': {4}}}
        assert result == ddiff

    def test_set_of_none(self):
        """
        https://github.com/seperman/deepdiff/issues/64
        """
        ddiff = DeepDiff(set(), {None})
        assert {'set_item_added': {'root[None]'}} == ddiff

    def test_list_that_contains_dictionary(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, {1: 1, 2: 2}]}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, {1: 3}]}}
        ddiff = DeepDiff(t1, t2)
        result = {
            'dictionary_item_removed': {"root[4]['b'][2][2]"},
            'values_changed': {
                "root[4]['b'][2][1]": {
                    'old_value': 1,
                    'new_value': 3
                }
            }
        }
        assert result == ddiff

    def test_dictionary_of_list_of_dictionary_ignore_order(self):
        t1 = {
            'item': [{
                'title': 1,
                'http://purl.org/rss/1.0/modules/content/:encoded': '1'
            }, {
                'title': 2,
                'http://purl.org/rss/1.0/modules/content/:encoded': '2'
            }]
        }

        t2 = {
            'item': [{
                'http://purl.org/rss/1.0/modules/content/:encoded': '1',
                'title': 1
            }, {
                'http://purl.org/rss/1.0/modules/content/:encoded': '2',
                'title': 2
            }]
        }

        ddiff = DeepDiff(t1, t2, ignore_order=True)
        assert {} == ddiff

    def test_comprehensive_ignore_order(self):

        t1 = {
            'key1': 'val1',
            'key2': [
                {
                    'key3': 'val3',
                    'key4': 'val4',
                },
                {
                    'key5': 'val5',
                    'key6': 'val6',
                },
            ],
        }

        t2 = {
            'key1': 'val1',
            'key2': [
                {
                    'key5': 'val5',
                    'key6': 'val6',
                },
                {
                    'key3': 'val3',
                    'key4': 'val4',
                },
            ],
        }

        ddiff = DeepDiff(t1, t2, ignore_order=True)
        assert {} == ddiff

    def test_ignore_order_when_objects_similar(self):
        """
        The current design can't recognize that

        {
            'key5': 'val5,
            'key6': 'val6',
        }

        at index 1

        has become

        {
            'key5': 'CHANGE',
            'key6': 'val6',
        }

        at index 0.

        Further thought needs to go into designing
        an algorithm that can identify the modified objects when ignoring order.

        The current algorithm computes the hash of the objects and since the hashes
        are different, it assumes an object is removed and another one is added.
        """

        t1 = {
            'key1': 'val1',
            'key2': [
                {
                    'key3': 'val3',
                    'key4': 'val4',
                },
                {
                    'key5': 'val5',
                    'key6': 'val6',
                },
            ],
        }

        t2 = {
            'key1': 'val1',
            'key2': [
                {
                    'key5': 'CHANGE',
                    'key6': 'val6',
                },
                {
                    'key3': 'val3',
                    'key4': 'val4',
                },
            ],
        }

        ddiff = DeepDiff(t1, t2, ignore_order=True)
        assert {
            'iterable_item_removed': {
                "root['key2'][1]": {
                    'key5': 'val5',
                    'key6': 'val6'
                }
            },
            'iterable_item_added': {
                "root['key2'][0]": {
                    'key5': 'CHANGE',
                    'key6': 'val6'
                }
            }
        } == ddiff

    def test_set_ignore_order_report_repetition(self):
        """
        If this test fails, it means that DeepDiff is not checking
        for set types before general iterables.
        So it forces creating the hashtable because of report_repetition=True.
        """
        t1 = {2, 1, 8}
        t2 = {1, 2, 3, 5}
        ddiff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True)
        result = {
            'set_item_added': {'root[3]', 'root[5]'},
            'set_item_removed': {'root[8]'}
        }
        assert result == ddiff

    def test_set(self):
        t1 = {1, 2, 8}
        t2 = {1, 2, 3, 5}
        ddiff = DeepDiff(t1, t2)
        result = {
            'set_item_added': {'root[3]', 'root[5]'},
            'set_item_removed': {'root[8]'}
        }
        assert result == ddiff

    def test_set_strings(self):
        t1 = {"veggies", "tofu"}
        t2 = {"veggies", "tofu", "seitan"}
        ddiff = DeepDiff(t1, t2)
        result = {'set_item_added': {"root['seitan']"}}
        assert result == ddiff

    def test_frozenset(self):
        t1 = frozenset([1, 2, 'B'])
        t2 = frozenset([1, 2, 3, 5])
        ddiff = DeepDiff(t1, t2)
        result = {
            'set_item_added': {'root[3]', 'root[5]'},
            'set_item_removed': {"root['B']"}
        }
        assert result == ddiff

    def test_tuple(self):
        t1 = (1, 2, 8)
        t2 = (1, 2, 3, 5)
        ddiff = DeepDiff(t1, t2)
        result = {
            'values_changed': {
                'root[2]': {
                    'old_value': 8,
                    'new_value': 3
                }
            },
            'iterable_item_added': {
                'root[3]': 5
            }
        }
        assert result == ddiff

    def test_named_tuples(self):
        from collections import namedtuple
        Point = namedtuple('Point', ['x', 'y'])
        t1 = Point(x=11, y=22)
        t2 = Point(x=11, y=23)
        ddiff = DeepDiff(t1, t2)
        result = {
            'values_changed': {
                'root.y': {
                    'old_value': 22,
                    'new_value': 23
                }
            }
        }
        assert result == ddiff

    def test_enums(self):
        from enum import Enum

        class MyEnum(Enum):
            A = 1
            B = 2

        ddiff = DeepDiff(MyEnum.A, MyEnum(1))
        result = {}
        assert ddiff == result

        ddiff = DeepDiff(MyEnum.A, MyEnum.B)
        result = {
            'values_changed': {
                'root._name_': {
                    'old_value': 'A',
                    'new_value': 'B'
                },
                'root._value_': {
                    'old_value': 1,
                    'new_value': 2
                }
            }
        }
        assert ddiff == result

    def test_custom_objects_change(self):
        t1 = CustomClass(1)
        t2 = CustomClass(2)
        ddiff = DeepDiff(t1, t2)
        result = {
            'values_changed': {
                'root.a': {
                    'old_value': 1,
                    'new_value': 2
                }
            }
        }
        assert result == ddiff

    def test_custom_objects2(self):
        cc_a = CustomClass2(prop1=["a"], prop2=["b"])
        cc_b = CustomClass2(prop1=["b"], prop2=["b"])
        t1 = [cc_a, CustomClass2(prop1=["c"], prop2=["d"])]
        t2 = [cc_b, CustomClass2(prop1=["c"], prop2=["d"])]

        ddiff = DeepDiff(t1, t2, ignore_order=True)

        result = {'iterable_item_added': {'root[0]': cc_b},
                  'iterable_item_removed': {'root[0]': cc_a}}

        assert result == ddiff

    def test_custom_objects_slot_change(self):
        class ClassA:
            __slots__ = ('x', 'y')

            def __init__(self, x, y):
                self.x = x
                self.y = y

        t1 = ClassA(1, 1)
        t2 = ClassA(1, 2)
        ddiff = DeepDiff(t1, t2)
        result = {
            'values_changed': {
                'root.y': {
                    'old_value': 1,
                    'new_value': 2
                }
            }
        }
        assert result == ddiff

    def test_custom_class_changes_with_slot_changes(self):
        class ClassA:
            __slots__ = ['x', 'y']

            def __init__(self, x, y):
                self.x = x
                self.y = y

        class ClassB:
            __slots__ = ['x']

        ddiff = DeepDiff(ClassA, ClassB)
        result = {'type_changes': {'root': {'old_type': ClassA, 'new_type': ClassB}}}
        assert result == ddiff

    def test_custom_class_changes_with_slot_change_when_ignore_type(self):
        class ClassA:
            __slots__ = ['x', 'y']

            def __init__(self, x, y):
                self.x = x
                self.y = y

        class ClassB:
            __slots__ = ['x']

        ddiff = DeepDiff(ClassA, ClassB, ignore_type_in_groups=[(ClassA, ClassB)])
        result = {'iterable_item_removed': {'root.__slots__[1]': 'y'}, 'attribute_removed': {'root.__init__', 'root.y'}}
        assert result == ddiff

    def test_custom_object_changes_when_ignore_type_in_groups(self):
        class ClassA:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        class ClassB:
            def __init__(self, x):
                self.x = x

        class ClassC(ClassB):
            def __repr__(self):
                return "obj c"

        obj_a = ClassA(1, 2)
        obj_c = ClassC(3)
        ddiff = DeepDiff(obj_a, obj_c, ignore_type_in_groups=[(ClassA, ClassB)], ignore_type_subclasses=False)
        result = {'type_changes': {'root': {'old_type': ClassA, 'new_type': ClassC, 'old_value': obj_a, 'new_value': obj_c}}}
        assert result == ddiff

        ddiff = DeepDiff(obj_a, obj_c, ignore_type_in_groups=[(ClassA, ClassB)], ignore_type_subclasses=True)
        result = {'values_changed': {'root.x': {'new_value': 3, 'old_value': 1}}, 'attribute_removed': ['root.y']}
        assert result == ddiff

    def test_custom_objects_slot_in_parent_class_change(self):
        class ClassA:
            __slots__ = ['x']

        class ClassB(ClassA):
            __slots__ = ['y']

            def __init__(self, x, y):
                self.x = x
                self.y = y

        t1 = ClassB(1, 1)
        t2 = ClassB(2, 1)
        ddiff = DeepDiff(t1, t2)
        result = {
            'values_changed': {
                'root.x': {
                    'old_value': 1,
                    'new_value': 2
                }
            }
        }
        assert result == ddiff

    def test_custom_objects_with_single_protected_slot(self):
        class ClassA:
            __slots__ = '__a'

            def __init__(self):
                self.__a = 1

            def __str__(self):
                return str(self.__a)

        t1 = ClassA()
        t2 = ClassA()
        ddiff = DeepDiff(t1, t2)
        assert {} == ddiff

    def test_custom_objects_with_weakref_in_slots(self):
        class ClassA:
            __slots__ = ['a', '__weakref__']

            def __init__(self, a):
                self.a = a

        t1 = ClassA(1)
        t2 = ClassA(2)
        diff = DeepDiff(t1, t2)
        result = {
            'values_changed': {
                'root.a': {
                    'new_value': 2,
                    'old_value': 1
                }
            },
        }
        assert result == diff

    def get_custom_objects_add_and_remove(self):
        class ClassA:
            a = 1

            def __init__(self, b):
                self.b = b
                self.d = 10

        t1 = ClassA(1)
        t2 = ClassA(2)
        t2.c = "new attribute"
        del t2.d
        return t1, t2

    def test_custom_objects_add_and_remove(self):
        t1, t2 = self.get_custom_objects_add_and_remove()
        ddiff = DeepDiff(t1, t2)
        result = {
            'attribute_added': {'root.c'},
            'values_changed': {
                'root.b': {
                    'new_value': 2,
                    'old_value': 1
                }
            },
            'attribute_removed': {'root.d'}
        }
        assert result == ddiff

    def test_custom_objects_add_and_remove_verbose(self):
        t1, t2 = self.get_custom_objects_add_and_remove()
        ddiff = DeepDiff(t1, t2, verbose_level=2)
        result = {
            'attribute_added': {
                'root.c': 'new attribute'
            },
            'attribute_removed': {
                'root.d': 10
            },
            'values_changed': {
                'root.b': {
                    'new_value': 2,
                    'old_value': 1
                }
            }
        }
        assert result == ddiff

    def get_custom_object_with_added_removed_methods(self):
        class ClassA:
            def method_a(self):
                pass

        t1 = ClassA()
        t2 = ClassA()

        def method_b(self):
            pass

        def method_c(self):
            return "hello"

        t2.method_b = method_b
        t2.method_a = method_c
        # Note that we are comparing ClassA instances. method_a originally was in ClassA
        # But we also added another version of it to t2. So it comes up as
        # added attribute.
        return t1, t2

    def test_custom_objects_add_and_remove_method(self):
        t1, t2 = self.get_custom_object_with_added_removed_methods()
        ddiff = DeepDiff(t1, t2)

        result = {'attribute_added': {'root.method_a', 'root.method_b'}}
        assert result == ddiff

    def test_custom_objects_add_and_remove_method_verbose(self):
        t1, t2 = self.get_custom_object_with_added_removed_methods()
        ddiff = DeepDiff(t1, t2, verbose_level=2)
        assert 'root.method_a' in ddiff['attribute_added']
        assert 'root.method_b' in ddiff['attribute_added']

    def test_set_of_custom_objects(self):
        member1 = CustomClass(13, 37)
        member2 = CustomClass(13, 37)
        t1 = {member1}
        t2 = {member2}
        ddiff = DeepDiff(t1, t2)
        result = {}
        assert result == ddiff

    def test_dictionary_of_custom_objects(self):
        member1 = CustomClass(13, 37)
        member2 = CustomClass(13, 37)
        t1 = {1: member1}
        t2 = {1: member2}
        ddiff = DeepDiff(t1, t2)
        result = {}
        assert result == ddiff

    def test_custom_object_type_change_when_ignore_order(self):

        class Burrito:
            bread = 'flour'

            def __init__(self):
                self.spicy = True

        class Taco:
            bread = 'flour'

            def __init__(self):
                self.spicy = True

        burrito = Burrito()
        taco = Taco()

        burritos = [burrito]
        tacos = [taco]

        assert not DeepDiff(burritos, tacos, ignore_type_in_groups=[(Taco, Burrito)], ignore_order=True)

    def test_loop(self):
        class LoopTest:
            def __init__(self, a):
                self.loop = self
                self.a = a

        t1 = LoopTest(1)
        t2 = LoopTest(2)

        ddiff = DeepDiff(t1, t2)
        result = {
            'values_changed': {
                'root.a': {
                    'old_value': 1,
                    'new_value': 2
                }
            }
        }
        assert result == ddiff

    def test_loop2(self):
        class LoopTestA:
            def __init__(self, a):
                self.loop = LoopTestB
                self.a = a

        class LoopTestB:
            def __init__(self, a):
                self.loop = LoopTestA
                self.a = a

        t1 = LoopTestA(1)
        t2 = LoopTestA(2)

        ddiff = DeepDiff(t1, t2)
        result = {
            'values_changed': {
                'root.a': {
                    'old_value': 1,
                    'new_value': 2
                }
            }
        }
        assert result == ddiff

    def test_loop3(self):
        class LoopTest:
            def __init__(self, a):
                self.loop = LoopTest
                self.a = a

        t1 = LoopTest(1)
        t2 = LoopTest(2)

        ddiff = DeepDiff(t1, t2)
        result = {
            'values_changed': {
                'root.a': {
                    'old_value': 1,
                    'new_value': 2
                }
            }
        }
        assert result == ddiff

    def test_loop_in_lists(self):
        t1 = [1, 2, 3]
        t1.append(t1)

        t2 = [1, 2, 4]
        t2.append(t2)

        ddiff = DeepDiff(t1, t2)
        result = {
            'values_changed': {
                'root[2]': {
                    'new_value': 4,
                    'old_value': 3
                }
            }
        }
        assert result == ddiff

    def test_loop_in_lists2(self):
        t1 = [1, 2, [3]]
        t1[2].append(t1)
        t2 = [1, 2, [4]]
        t2[2].append(t2)

        ddiff = DeepDiff(t1, t2)
        result = {
            'values_changed': {
                'root[2][0]': {
                    'old_value': 3,
                    'new_value': 4
                }
            }
        }
        assert result == ddiff

    def test_decimal(self):
        t1 = {1: Decimal('10.1')}
        t2 = {1: Decimal('2.2')}
        ddiff = DeepDiff(t1, t2)
        result = {
            'values_changed': {
                'root[1]': {
                    'new_value': Decimal('2.2'),
                    'old_value': Decimal('10.1')
                }
            }
        }
        assert result == ddiff

    def test_decimal_ignore_order(self):
        t1 = [{1: Decimal('10.1')}, {2: Decimal('10.2')}]
        t2 = [{2: Decimal('10.2')}, {1: Decimal('10.1')}]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        result = {}
        assert result == ddiff

    def test_unicode_string_type_changes(self):
        """
        These tests were written when DeepDiff was in Python 2.
        Writing b"你好" throws an exception in Python 3 so can't be used for testing.
        These tests are currently useless till they are rewritten properly.
        """
        unicode_string = {"hello": "你好"}
        ascii_string = {"hello": "你好"}
        ddiff = DeepDiff(unicode_string, ascii_string)
        result = {}
        assert result == ddiff

    def test_unicode_string_value_changes(self):
        unicode_string = {"hello": "你好"}
        ascii_string = {"hello": "你好hello"}
        ddiff = DeepDiff(unicode_string, ascii_string)
        result = {
            'values_changed': {
                "root['hello']": {
                    'old_value': '你好',
                    'new_value': '你好hello'
                }
            }
        }
        assert result == ddiff

    def test_unicode_string_value_and_type_changes(self):
        unicode_string = {"hello": "你好"}
        ascii_string = {"hello": "你好hello"}
        ddiff = DeepDiff(unicode_string, ascii_string)
        # In python3, all string is unicode, so these 2 strings only diff
        # in values
        result = {
            'values_changed': {
                "root['hello']": {
                    'new_value': '你好hello',
                    'old_value': '你好'
                }
            }
        }
        assert result == ddiff

    def test_int_to_unicode_string(self):
        t1 = 1
        ascii_string = "你好"
        ddiff = DeepDiff(t1, ascii_string)
        # In python3, all string is unicode, so these 2 strings only diff
        # in values
        result = {
            'type_changes': {
                'root': {
                    'old_type': int,
                    'new_type': str,
                    'old_value': 1,
                    'new_value': '你好'
                }
            }
        }
        assert result == ddiff

    def test_int_to_unicode(self):
        t1 = 1
        unicode_string = "你好"
        ddiff = DeepDiff(t1, unicode_string)
        # In python3, all string is unicode, so these 2 strings only diff
        # in values
        result = {
            'type_changes': {
                'root': {
                    'old_type': int,
                    'new_type': str,
                    'old_value': 1,
                    'new_value': '你好'
                }
            }
        }
        assert result == ddiff

    @pytest.mark.parametrize("t1, t2, ignore_numeric_type_changes, significant_digits, number_format_notation, result", [
        (Decimal('2.5'), Decimal('1.5'), False, 0, "f", {}),
        (Decimal('2.5'), Decimal('1.5'), False, 1, "f", {'values_changed': {'root': {'new_value': Decimal('1.5'), 'old_value': Decimal('2.5')}}}),
        (Decimal('2.5'), Decimal(2.5), False, 3, "f", {}),
        (1024, 1022, False, 2, "e", {}),
        ({"key": [Decimal('2.0001'), Decimal('20000.0001')]}, {"key": [2.0002, 20000.0002]}, True, 4, "e", {'values_changed': {"root['key'][0]": {'new_value': 2.0002, 'old_value': Decimal('2.0001')}}})
    ])
    def test_significant_digits_and_notation(self, t1, t2, ignore_numeric_type_changes, significant_digits, number_format_notation, result):
        ddiff = DeepDiff(t1, t2, significant_digits=significant_digits, number_format_notation=number_format_notation,
                         ignore_numeric_type_changes=ignore_numeric_type_changes)
        assert result == ddiff

    def test_significant_digits_for_complex_imaginary_part(self):
        t1 = 1.23 + 1.222254j
        t2 = 1.23 + 1.222256j
        ddiff = DeepDiff(t1, t2, significant_digits=4)
        assert {} == ddiff
        result = {
            'values_changed': {
                'root': {
                    'new_value': (1.23 + 1.222256j),
                    'old_value': (1.23 + 1.222254j)
                }
            }
        }
        ddiff = DeepDiff(t1, t2, significant_digits=5)
        assert result == ddiff

    def test_significant_digits_for_complex_real_part(self):
        t1 = 1.23446879 + 1.22225j
        t2 = 1.23446764 + 1.22225j
        ddiff = DeepDiff(t1, t2, significant_digits=5)
        assert {} == ddiff

    def test_significant_digits_for_list_of_floats(self):
        t1 = [1.2344, 5.67881, 6.778879]
        t2 = [1.2343, 5.67882, 6.778878]
        ddiff = DeepDiff(t1, t2, significant_digits=3)
        assert {} == ddiff
        ddiff = DeepDiff(t1, t2, significant_digits=4)
        result = {
            'values_changed': {
                'root[0]': {
                    'new_value': 1.2343,
                    'old_value': 1.2344
                }
            }
        }
        assert result == ddiff
        ddiff = DeepDiff(t1, t2, significant_digits=5)
        result = {
            'values_changed': {
                'root[0]': {
                    'new_value': 1.2343,
                    'old_value': 1.2344
                },
                'root[1]': {
                    'new_value': 5.67882,
                    'old_value': 5.67881
                }
            }
        }
        assert result == ddiff
        ddiff = DeepDiff(t1, t2)
        ddiff2 = DeepDiff(t1, t2, significant_digits=6)
        assert ddiff2 == ddiff

    def test_negative_significant_digits(self):
        with pytest.raises(ValueError):
            DeepDiff(1, 1, significant_digits=-1)

    @pytest.mark.parametrize("t1, t2, significant_digits, ignore_order", [
        (100000, 100021, 3, False),
        ([10, 12, 100000], [50, 63, 100021], 3, False),
        ([10, 12, 100000], [50, 63, 100021], 3, True),
    ])
    def test_number_to_string_func(self, t1, t2, significant_digits, ignore_order):
        def custom_number_to_string(number, *args, **kwargs):
            number = 100 if number < 100 else number
            return number_to_string(number, *args, **kwargs)

        ddiff = DeepDiff(t1, t2, significant_digits=3, number_format_notation="e",
                         number_to_string_func=custom_number_to_string)

        assert {} == ddiff

    @pytest.mark.parametrize("t1, t2, significant_digits, expected_result",
                             [
                                 (10, 10.0, 5, {}),
                                 (10, 10.2, 5, {'values_changed': {'root': {'new_value': 10.2, 'old_value': 10}}}),
                                 (10, 10.2, 0, {}),
                                 (Decimal(10), 10, 0, {}),
                                 (Decimal(10), 10, 10, {}),
                                 (Decimal(10), 10.0, 0, {}),
                                 (Decimal(10), 10.0, 10, {}),
                                 (Decimal('10.0'), 10.0, 5, {}),
                                 (Decimal('10.01'), 10.01, 1, {}),
                                 (Decimal('10.01'), 10.01, 2, {}),
                                 (Decimal('10.01'), 10.01, 5, {}),
                                 (Decimal('10.01'), 10.01, 8, {}),
                                 (Decimal('10.010'), 10.01, 3, {}),
                                 (Decimal('100000.1'), 100000.1, 0, {}),
                                 (Decimal('100000.1'), 100000.1, 1, {}),
                                 (Decimal('100000.1'), 100000.1, 5, {}),
                                 (Decimal('100000'), 100000.1, 0, {}),
                                 (Decimal('100000'), 100000.1, 1, {'values_changed': {'root': {'new_value': 100000.1, 'old_value': Decimal('100000')}}}),
                             ])
    def test_decimal_digits(self, t1, t2, significant_digits, expected_result):
        ddiff = DeepDiff(t1, t2, ignore_numeric_type_changes=True, ignore_string_type_changes=True, significant_digits=significant_digits)
        assert expected_result == ddiff

    def test_ignore_type_in_groups(self):
        t1 = [1, 2, 3]
        t2 = [1.0, 2.0, 3.0]
        ddiff = DeepDiff(t1, t2, ignore_type_in_groups=DeepDiff.numbers)
        assert not ddiff

    def test_ignore_type_in_groups2(self):
        t1 = [1, 2, 3]
        t2 = [1.0, 2.0, 3.3]
        ddiff = DeepDiff(t1, t2, ignore_type_in_groups=DeepDiff.numbers)
        result = {'values_changed': {'root[2]': {'new_value': 3.3, 'old_value': 3}}}
        assert result == ddiff

    def test_ignore_type_in_groups_just_numbers(self):
        t1 = [1, 2, 3, 'a']
        t2 = [1.0, 2.0, 3.3, b'a']
        ddiff = DeepDiff(t1, t2, ignore_type_in_groups=[DeepDiff.numbers])
        result = {'values_changed': {'root[2]': {'new_value': 3.3, 'old_value': 3}},
                  'type_changes': {'root[3]': {'new_type': bytes,
                                               'new_value': b'a',
                                               'old_type': str,
                                               'old_value': 'a'}}
                  }
        assert result == ddiff

    def test_ignore_type_in_groups_numbers_and_strings(self):
        t1 = [1, 2, 3, 'a']
        t2 = [1.0, 2.0, 3.3, b'a']
        ddiff = DeepDiff(t1, t2, ignore_type_in_groups=[DeepDiff.numbers, DeepDiff.strings])
        result = {'values_changed': {'root[2]': {'new_value': 3.3, 'old_value': 3}}}
        assert result == ddiff

    def test_ignore_type_in_groups_numbers_and_strings_when_ignore_order(self):
        t1 = [1, 2, 3, 'a']
        t2 = [1.0, 2.0, 3.3, b'a']
        ddiff = DeepDiff(t1, t2, ignore_numeric_type_changes=True, ignore_string_type_changes=True, ignore_order=True)
        result = {'iterable_item_added': {'root[2]': 3.3}, 'iterable_item_removed': {'root[2]': 3}}
        assert result == ddiff

    def test_ignore_type_in_groups_none_and_objects(self):
        t1 = [1, 2, 3, 'a', None]
        t2 = [1.0, 2.0, 3.3, b'a', 'hello']
        ddiff = DeepDiff(t1, t2, ignore_type_in_groups=[(1, 1.0), (None, str, bytes)])
        result = {'values_changed': {'root[2]': {'new_value': 3.3, 'old_value': 3}}}
        assert result == ddiff

    def test_ignore_type_in_groups_str_and_datetime(self):
        now = datetime.datetime.utcnow()
        t1 = [1, 2, 3, 'a', now]
        t2 = [1, 2, 3, 'a', 'now']
        ddiff = DeepDiff(t1, t2, ignore_type_in_groups=[(str, bytes, datetime.datetime)])
        result = {'values_changed': {'root[4]': {'new_value': 'now', 'old_value': now}}}
        assert result == ddiff

    def test_ignore_string_type_changes_when_dict_keys_merge_is_not_deterministic(self):
        t1 = {'a': 10, b'a': 20}
        t2 = {'a': 11, b'a': 22}
        ddiff = DeepDiff(t1, t2, ignore_numeric_type_changes=True, ignore_string_type_changes=True, ignore_order=True)
        result = {'values_changed': {"root['a']": {'new_value': 22, 'old_value': 20}}}
        alternative_result = {'values_changed': {"root['a']": {'new_value': 11, 'old_value': 10}}}
        assert result == ddiff or alternative_result == ddiff

    @pytest.mark.parametrize("t1, t2, significant_digits, result", [
        ([0.1], [Decimal('0.10')], 55,
            {'values_changed': {'root[0]': {'new_value': Decimal('0.10'), 'old_value': 0.1}}}),  # Due to floating point arithmetics with high significant digits.
        ([0.1], [Decimal('0.10')], 5, {}),  # Same inputs as above but with significant digits that is low.
        ([-0.1], [-Decimal('0.10')], 5, {}),
        ([-Decimal('0.102')], [-Decimal('0.10')], 2, {}),
        ([1], [Decimal('1.00000002')], 3, {}),
    ])
    def test_ignore_type_in_groups_numbers_when_decimal(self, t1, t2, significant_digits, result):
        ddiff = DeepDiff(t1, t2, ignore_numeric_type_changes=True, significant_digits=significant_digits)
        assert result == ddiff

    @pytest.mark.skip(reason="REMAPPING DISABLED UNTIL KEY NAMES CHANGE AGAIN IN FUTURE")
    def test_base_level_dictionary_remapping(self):
        """
        Since subclassed dictionaries that override __getitem__ treat newdict.get(key)
        differently than newdict['key'], we are unable to create a unittest with
        self.assertIn() and have to resort to fetching the values of two keys and making
        sure they are the same value.
        """
        t1 = {1: 1, 2: 2}
        t2 = {2: 2, 3: 3}
        ddiff = DeepDiff(t1, t2)
        assert ddiff['dic_item_added'] == ddiff['dictionary_item_added']
        assert ddiff['dic_item_removed'] == ddiff['dictionary_item_removed']

    @pytest.mark.skip(reason="REMAPPING DISABLED UNTIL KEY NAMES CHANGE AGAIN IN FUTURE")
    def test_index_and_repeat_dictionary_remapping(self):
        t1 = [1, 3, 1, 4]
        t2 = [4, 4, 1]
        ddiff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True)
        assert ddiff['repetition_change']['root[0]']['newindexes'] == ddiff['repetition_change']['root[0]']['new_indexes']
        assert ddiff['repetition_change']['root[0]']['newrepeat'] == ddiff['repetition_change']['root[0]']['new_repeat']
        assert ddiff['repetition_change']['root[0]']['oldindexes'] == ddiff['repetition_change']['root[0]']['old_indexes']
        assert ddiff['repetition_change']['root[0]']['oldrepeat'] == ddiff['repetition_change']['root[0]']['old_repeat']

    @pytest.mark.skip(reason="REMAPPING DISABLED UNTIL KEY NAMES CHANGE AGAIN IN FUTURE")
    def test_value_and_type_dictionary_remapping(self):
        t1 = {1: 1, 2: 2}
        t2 = {1: 1, 2: '2'}
        ddiff = DeepDiff(t1, t2)
        assert ddiff['type_changes']['root[2]']['newtype'] == ddiff['type_changes']['root[2]']['new_type']
        assert ddiff['type_changes']['root[2]']['newvalue'] == ddiff['type_changes']['root[2]']['new_value']
        assert ddiff['type_changes']['root[2]']['oldtype'] == ddiff['type_changes']['root[2]']['old_type']
        assert ddiff['type_changes']['root[2]']['oldvalue'] == ddiff['type_changes']['root[2]']['old_value']

    def test_skip_type(self):
        l1 = logging.getLogger("test")
        l2 = logging.getLogger("test2")
        t1 = {"log": l1, 2: 1337}
        t2 = {"log": l2, 2: 1337}
        ddiff = DeepDiff(t1, t2, exclude_types={logging.Logger})
        assert {} == ddiff

        t1 = {"log": "book", 2: 1337}
        t2 = {"log": l2, 2: 1337}
        ddiff = DeepDiff(t1, t2, exclude_types={logging.Logger})
        assert {} == ddiff

    def test_skip_path1(self):
        t1 = {
            "for life": "vegan",
            "ingredients": ["no meat", "no eggs", "no dairy"]
        }
        t2 = {
            "for life": "vegan",
            "ingredients": ["veggies", "tofu", "soy sauce"]
        }
        ddiff = DeepDiff(t1, t2, exclude_paths={"root['ingredients']"})
        assert {} == ddiff

    def test_skip_path2(self):
        t1 = {
            "for life": "vegan",
            "ingredients": ["no meat", "no eggs", "no dairy"]
        }
        t2 = {"for life": "vegan"}
        ddiff = DeepDiff(t1, t2, exclude_paths={"root['ingredients']"})
        assert {} == ddiff

    def test_skip_path2_reverse(self):
        t1 = {
            "for life": "vegan",
            "ingredients": ["no meat", "no eggs", "no dairy"]
        }
        t2 = {"for life": "vegan"}
        ddiff = DeepDiff(t2, t1, exclude_paths={"root['ingredients']"})
        assert {} == ddiff

    def test_skip_path4(self):
        t1 = {
            "for life": "vegan",
            "ingredients": ["no meat", "no eggs", "no dairy"]
        }
        t2 = {"for life": "vegan", "zutaten": ["veggies", "tofu", "soy sauce"]}
        ddiff = DeepDiff(t1, t2, exclude_paths={"root['ingredients']"})
        assert 'dictionary_item_added' in ddiff, {}
        assert 'dictionary_item_removed' not in ddiff, {}

    def test_skip_custom_object_path(self):
        t1 = CustomClass(1)
        t2 = CustomClass(2)
        ddiff = DeepDiff(t1, t2, exclude_paths=['root.a'])
        result = {}
        assert result == ddiff

    def test_skip_list_path(self):
        t1 = ['a', 'b']
        t2 = ['a']
        ddiff = DeepDiff(t1, t2, exclude_paths=['root[1]'])
        result = {}
        assert result == ddiff

    def test_skip_dictionary_path(self):
        t1 = {1: {2: "a"}}
        t2 = {1: {}}
        ddiff = DeepDiff(t1, t2, exclude_paths=['root[1][2]'])
        result = {}
        assert result == ddiff

    def test_skip_dictionary_path_with_custom_object(self):
        obj1 = CustomClass(1)
        obj2 = CustomClass(2)

        t1 = {1: {2: obj1}}
        t2 = {1: {2: obj2}}
        ddiff = DeepDiff(t1, t2, exclude_paths=['root[1][2].a'])
        result = {}
        assert result == ddiff

    def test_skip_regexp(self):
        t1 = [{'a': 1, 'b': 2}, {'c': 4, 'b': 5}]
        t2 = [{'a': 1, 'b': 3}, {'c': 4, 'b': 5}]
        ddiff = DeepDiff(t1, t2, exclude_regex_paths=[r"root\[\d+\]\['b'\]"])
        result = {}
        assert result == ddiff

    def test_skip_str_type_in_dictionary(self):
        t1 = {1: {2: "a"}}
        t2 = {1: {}}
        ddiff = DeepDiff(t1, t2, exclude_types=[str])
        result = {}
        assert result == ddiff

    def test_skip_str_type_in_dict_on_list(self):
        t1 = [{1: "a"}]
        t2 = [{}]
        ddiff = DeepDiff(t1, t2, exclude_types=[str])
        result = {}
        assert result == ddiff

    def test_skip_str_type_in_dict_on_list_when_ignored_order(self):
        t1 = [{1: "a"}]
        t2 = [{}]
        ddiff = DeepDiff(t1, t2, exclude_types=[str], ignore_order=True)
        result = {}
        assert result == ddiff

    def test_unknown_parameters(self):
        with pytest.raises(ValueError):
            DeepDiff(1, 1, wrong_param=2)

    def test_bad_attribute(self):
        class Bad:
            __slots__ = ['x', 'y']

            def __getattr__(self, key):
                raise AttributeError("Bad item")

            def __str__(self):
                return "Bad Object"

        t1 = Bad()
        t2 = Bad()

        ddiff = DeepDiff(t1, t2)
        result = {'unprocessed': ['root: Bad Object and Bad Object']}
        assert result == ddiff

    def test_dict_none_item_removed(self):
        t1 = {1: None, 2: 2}
        t2 = {2: 2}
        ddiff = DeepDiff(t1, t2)
        result = {
            'dictionary_item_removed': {'root[1]'}
        }
        assert result == ddiff

    def test_list_none_item_removed(self):
        t1 = [1, 2, None]
        t2 = [1, 2]
        ddiff = DeepDiff(t1, t2)
        result = {
            'iterable_item_removed': {'root[2]': None}
        }
        assert result == ddiff

    def test_non_subscriptable_iterable(self):
        def gen1():
            yield 42
            yield 1337
            yield 31337

        def gen2():
            yield 42
            yield 1337

        t1 = gen1()
        t2 = gen2()
        ddiff = DeepDiff(t1, t2)

        result = {'iterable_item_removed': {'root[2]': 31337}}
        # Note: In text-style results, we currently pretend this stuff is subscriptable for readability

        assert result == ddiff

    @mock.patch('deepdiff.diff.logger')
    @mock.patch('deepdiff.diff.DeepHash')
    def test_diff_when_hash_fails(self, mock_DeepHash, mock_logger):
        mock_DeepHash.side_effect = Exception('Boom!')
        t1 = {"blah": {4}, 2: 1337}
        t2 = {"blah": {4}, 2: 1337}
        DeepDiff(t1, t2, ignore_order=True)
        assert mock_logger.error.called

    def test_bool_vs_number(self):
        t1 = {
            "A List": [
                {
                    "Value One": True,
                    "Value Two": 1
                }
            ],
        }

        t2 = {
            "A List": [
                {
                    "Value Two": 1,
                    "Value One": True
                }
            ],
        }

        ddiff = DeepDiff(t1, t2, ignore_order=True)
        assert ddiff == {}

    @pytest.mark.parametrize('t1, t2, params, expected_result', [
        (float('nan'), float('nan'), {}, ['values_changed']),
        (float('nan'), float('nan'), {'ignore_nan_inequality': True}, []),
        ([1, float('nan')], [1, float('nan')], {'ignore_nan_inequality': True}, []),
    ])
    @pytest.mark.skipif(pypy3, reason="some versions of pypy3 have nan==nan")
    def test_ignore_nan_inequality(self, t1, t2, params, expected_result):
        assert expected_result == list(DeepDiff(t1, t2, **params).keys())
