#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
To run only the search tests:
    python -m unittest tests.test_diff_text

Or to run all the tests:
    python -m unittest discover

Or to run all the tests with coverage:
    coverage run --source deepdiff setup.py test

Or using Nose:
    nosetests --with-coverage --cover-package=deepdiff

To run a specific test, run this from the root of repo:
    python -m unittest tests.test_diff_text.DeepDiffTextTestCase.test_same_objects

or using nosetests:
    nosetests tests/test_diff_text.py:DeepDiffTestCase.test_diff_when_hash_fails
"""
import unittest
import datetime
from decimal import Decimal
from deepdiff import DeepDiff
from deepdiff.helper import py3
from tests import CustomClass
if py3:
    from unittest import mock
else:
    import mock

import logging
logging.disable(logging.CRITICAL)


class DeepDiffTextTestCase(unittest.TestCase):
    """DeepDiff Tests."""

    def test_same_objects(self):
        t1 = {1: 1, 2: 2, 3: 3}
        t2 = t1
        self.assertEqual(DeepDiff(t1, t2), {})

    def test_item_type_change(self):
        t1 = {1: 1, 2: 2, 3: 3}
        t2 = {1: 1, 2: "2", 3: 3}
        ddiff = DeepDiff(t1, t2)
        self.assertEqual(ddiff, {
            'type_changes': {
                "root[2]": {
                    "old_value": 2,
                    "old_type": int,
                    "new_value": "2",
                    "new_type": str
                }
            }
        })

    def test_item_type_change_less_verbose(self):
        t1 = {1: 1, 2: 2, 3: 3}
        t2 = {1: 1, 2: "2", 3: 3}
        self.assertEqual(
            DeepDiff(
                t1, t2, verbose_level=0),
            {'type_changes': {
                "root[2]": {
                    "old_type": int,
                    "new_type": str
                }
            }})

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
        self.assertEqual(DeepDiff(t1, t2), result)

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
        self.assertEqual(ddiff, result)

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
        self.assertEqual(ddiff, result)

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
        self.assertEqual(ddiff, result)

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
        self.assertEqual(ddiff, result)

    def test_diffs_equal_strings_when_not_identical(self):
        t1 = 'hello'
        t2 = 'hel'
        t2 += 'lo'
        assert t1 is not t2
        ddiff = DeepDiff(t1, t2)
        self.assertEqual(ddiff, {})

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
        self.assertEqual(ddiff, result)

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
        self.assertEqual(ddiff, result)

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
        self.assertEqual(ddiff, result)

    def test_list_difference_add(self):
        t1 = [1, 2]
        t2 = [1, 2, 3, 5]
        ddiff = DeepDiff(t1, t2)
        result = {'iterable_item_added': {'root[2]': 3, 'root[3]': 5}}
        self.assertEqual(ddiff, result)

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
        self.assertEqual(ddiff, result)

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
        self.assertEqual(ddiff, result)

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
        self.assertEqual(ddiff, result)

    def test_list_difference_ignore_order(self):
        t1 = {1: 1, 4: {"a": "hello", "b": [1, 2, 3]}}
        t2 = {1: 1, 4: {"a": "hello", "b": [1, 3, 2, 3]}}
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        self.assertEqual(ddiff, {})

    def test_dictionary_difference_ignore_order(self):
        t1 = {"a": [[{"b": 2, "c": 4}, {"b": 2, "c": 3}]]}
        t2 = {"a": [[{"b": 2, "c": 3}, {"b": 2, "c": 4}]]}
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        self.assertEqual(ddiff, {})

    def test_nested_list_ignore_order(self):
        t1 = [1, 2, [3, 4]]
        t2 = [[4, 3, 3], 2, 1]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        self.assertEqual(ddiff, {})

    def test_nested_list_difference_ignore_order(self):
        t1 = [1, 2, [3, 4]]
        t2 = [[4, 3], 2, 1]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        self.assertEqual(ddiff, {})

    def test_nested_list_with_dictionarry_difference_ignore_order(self):
        t1 = [1, 2, [3, 4, {1: 2}]]
        t2 = [[4, 3, {1: 2}], 2, 1]

        ddiff = DeepDiff(t1, t2, ignore_order=True)

        result = {}
        self.assertEqual(ddiff, result)

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
        self.assertEqual(ddiff, result)

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
        self.assertNotEqual(ddiff, result)

    def test_list_of_unhashable_difference_ignore_order(self):
        t1 = [{"a": 2}, {"b": [3, 4, {1: 1}]}]
        t2 = [{"b": [3, 4, {1: 1}]}, {"a": 2}]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        self.assertEqual(ddiff, {})

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
        self.assertEqual(ddiff, result)

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
        self.assertEqual(ddiff, result)

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
        self.assertEqual(ddiff, result)

    def test_list_of_unhashable_difference_ignore_order4(self):
        t1 = [{"a": 2}, {"a": 2}]
        t2 = [{"a": 2}]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        result = {}
        self.assertEqual(ddiff, result)

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
        self.assertEqual(ddiff, result)

    def test_list_of_sets_difference_ignore_order(self):
        t1 = [{1}, {2}, {3}]
        t2 = [{4}, {1}, {2}, {3}]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        result = {'iterable_item_added': {'root[0]': {4}}}
        self.assertEqual(ddiff, result)

    def test_list_of_sets_difference_ignore_order_when_there_is_duplicate(
            self):
        t1 = [{1}, {2}, {3}]
        t2 = [{4}, {1}, {2}, {3}, {3}]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        result = {'iterable_item_added': {'root[0]': {4}}}
        self.assertEqual(ddiff, result)

    def test_list_of_sets_difference_ignore_order_when_there_is_duplicate_and_mix_of_hashable_unhashable(
            self):
        t1 = [1, 1, {2}, {3}]
        t2 = [{4}, 1, {2}, {3}, {3}, 1, 1]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        result = {'iterable_item_added': {'root[0]': {4}}}
        self.assertEqual(ddiff, result)

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
        self.assertEqual(ddiff, result)

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
        self.assertEqual(ddiff, {})

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
        self.assertEqual(ddiff, {})

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
        self.assertEqual(ddiff, {
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
        })

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
        self.assertEqual(ddiff, result)

    def test_set(self):
        t1 = {1, 2, 8}
        t2 = {1, 2, 3, 5}
        ddiff = DeepDiff(t1, t2)
        result = {
            'set_item_added': {'root[3]', 'root[5]'},
            'set_item_removed': {'root[8]'}
        }
        self.assertEqual(ddiff, result)

    def test_set_strings(self):
        t1 = {"veggies", "tofu"}
        t2 = {"veggies", "tofu", "seitan"}
        ddiff = DeepDiff(t1, t2)
        result = {'set_item_added': {"root['seitan']"}}
        self.assertEqual(ddiff, result)

    def test_frozenset(self):
        t1 = frozenset([1, 2, 'B'])
        t2 = frozenset([1, 2, 3, 5])
        ddiff = DeepDiff(t1, t2)
        result = {
            'set_item_added': {'root[3]', 'root[5]'},
            'set_item_removed': {"root['B']"}
        }
        self.assertEqual(ddiff, result)

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
        self.assertEqual(ddiff, result)

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
        self.assertEqual(ddiff, result)

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
        self.assertEqual(ddiff, result)

    def test_custom_objects_slot_change(self):
        class ClassA(object):
            __slots__ = ['x', 'y']

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
        self.assertEqual(ddiff, result)

    def test_custom_objects_with_single_protected_slot(self):
        class ClassA(object):
            __slots__ = '__a'

            def __init__(self):
                self.__a = 1

            def __str__(self):
                return str(self.__a)

        t1 = ClassA()
        t2 = ClassA()
        diff = DeepDiff(t1, t2)
        self.assertEqual(diff, {})

    def get_custom_objects_add_and_remove(self):
        class ClassA(object):
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
        self.assertEqual(ddiff, result)

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
        self.assertEqual(ddiff, result)

    def get_custom_object_with_added_removed_methods(self):
        class ClassA(object):
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
        self.assertEqual(ddiff, result)

    def test_custom_objects_add_and_remove_method_verbose(self):
        t1, t2 = self.get_custom_object_with_added_removed_methods()
        ddiff = DeepDiff(t1, t2, verbose_level=2)
        self.assertTrue('root.method_a' in ddiff['attribute_added'])
        self.assertTrue('root.method_b' in ddiff['attribute_added'])

    def test_set_of_custom_objects(self):
        member1 = CustomClass(13, 37)
        member2 = CustomClass(13, 37)
        t1 = {member1}
        t2 = {member2}
        ddiff = DeepDiff(t1, t2)
        result = {}
        self.assertEqual(ddiff, result)

    def test_dictionary_of_custom_objects(self):
        member1 = CustomClass(13, 37)
        member2 = CustomClass(13, 37)
        t1 = {1: member1}
        t2 = {1: member2}
        ddiff = DeepDiff(t1, t2)
        result = {}
        self.assertEqual(ddiff, result)

    def test_loop(self):
        class LoopTest(object):
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
        self.assertEqual(ddiff, result)

    def test_loop2(self):
        class LoopTestA(object):
            def __init__(self, a):
                self.loop = LoopTestB
                self.a = a

        class LoopTestB(object):
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
        self.assertEqual(ddiff, result)

    def test_loop3(self):
        class LoopTest(object):
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
        self.assertEqual(ddiff, result)

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
        self.assertEqual(ddiff, result)

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
        self.assertEqual(ddiff, result)

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
        self.assertEqual(ddiff, result)

    def test_decimal_ignore_order(self):
        t1 = [{1: Decimal('10.1')}, {2: Decimal('10.2')}]
        t2 = [{2: Decimal('10.2')}, {1: Decimal('10.1')}]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        result = {}
        self.assertEqual(ddiff, result)

    def test_unicode_string_type_changes(self):
        unicode_string = {"hello": u"你好"}
        ascii_string = {"hello": "你好"}
        ddiff = DeepDiff(unicode_string, ascii_string)
        if py3:
            # In python3, all string is unicode, so diff is empty
            result = {}
        else:
            # In python2, these are 2 different type of strings
            result = {
                'type_changes': {
                    "root['hello']": {
                        'old_type': unicode,
                        'new_value': '\xe4\xbd\xa0\xe5\xa5\xbd',
                        'old_value': u'\u4f60\u597d',
                        'new_type': str
                    }
                }
            }
        self.assertEqual(ddiff, result)

    def test_unicode_string_value_changes(self):
        unicode_string = {"hello": u"你好"}
        ascii_string = {"hello": u"你好hello"}
        ddiff = DeepDiff(unicode_string, ascii_string)
        if py3:
            result = {
                'values_changed': {
                    "root['hello']": {
                        'old_value': '你好',
                        'new_value': '你好hello'
                    }
                }
            }
        else:
            result = {
                'values_changed': {
                    "root['hello']": {
                        'new_value': u'\u4f60\u597dhello',
                        'old_value': u'\u4f60\u597d'
                    }
                }
            }
        self.assertEqual(ddiff, result)

    def test_unicode_string_value_and_type_changes(self):
        unicode_string = {"hello": u"你好"}
        ascii_string = {"hello": "你好hello"}
        ddiff = DeepDiff(unicode_string, ascii_string)
        if py3:
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
        else:
            # In python2, these are 2 different type of strings
            result = {
                'type_changes': {
                    "root['hello']": {
                        'old_type': unicode,
                        'new_value': '\xe4\xbd\xa0\xe5\xa5\xbdhello',
                        'old_value': u'\u4f60\u597d',
                        'new_type': str
                    }
                }
            }
        self.assertEqual(ddiff, result)

    def test_int_to_unicode_string(self):
        t1 = 1
        ascii_string = "你好"
        ddiff = DeepDiff(t1, ascii_string)
        if py3:
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
        else:
            # In python2, these are 2 different type of strings
            result = {
                'type_changes': {
                    'root': {
                        'old_type': int,
                        'new_value': '\xe4\xbd\xa0\xe5\xa5\xbd',
                        'old_value': 1,
                        'new_type': str
                    }
                }
            }
        self.assertEqual(ddiff, result)

    def test_int_to_unicode(self):
        t1 = 1
        unicode_string = u"你好"
        ddiff = DeepDiff(t1, unicode_string)
        if py3:
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
        else:
            # In python2, these are 2 different type of strings
            result = {
                'type_changes': {
                    'root': {
                        'old_type': int,
                        'new_value': u'\u4f60\u597d',
                        'old_value': 1,
                        'new_type': unicode
                    }
                }
            }
        self.assertEqual(ddiff, result)

    def test_significant_digits_for_decimals(self):
        t1 = Decimal('2.5')
        t2 = Decimal('1.5')
        ddiff = DeepDiff(t1, t2, significant_digits=0)
        self.assertEqual(ddiff, {})

    def test_significant_digits_for_complex_imaginary_part(self):
        t1 = 1.23 + 1.222254j
        t2 = 1.23 + 1.222256j
        ddiff = DeepDiff(t1, t2, significant_digits=4)
        self.assertEqual(ddiff, {})
        result = {
            'values_changed': {
                'root': {
                    'new_value': (1.23 + 1.222256j),
                    'old_value': (1.23 + 1.222254j)
                }
            }
        }
        ddiff = DeepDiff(t1, t2, significant_digits=5)
        self.assertEqual(ddiff, result)

    def test_significant_digits_for_complex_real_part(self):
        t1 = 1.23446879 + 1.22225j
        t2 = 1.23446764 + 1.22225j
        ddiff = DeepDiff(t1, t2, significant_digits=5)
        self.assertEqual(ddiff, {})

    def test_significant_digits_for_list_of_floats(self):
        t1 = [1.2344, 5.67881, 6.778879]
        t2 = [1.2343, 5.67882, 6.778878]
        ddiff = DeepDiff(t1, t2, significant_digits=3)
        self.assertEqual(ddiff, {})
        ddiff = DeepDiff(t1, t2, significant_digits=4)
        result = {
            'values_changed': {
                'root[0]': {
                    'new_value': 1.2343,
                    'old_value': 1.2344
                }
            }
        }
        self.assertEqual(ddiff, result)
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
        self.assertEqual(ddiff, result)
        ddiff = DeepDiff(t1, t2)
        ddiff2 = DeepDiff(t1, t2, significant_digits=6)
        self.assertEqual(ddiff, ddiff2)

    def test_negative_significant_digits(self):
        with self.assertRaises(ValueError):
            DeepDiff(1, 1, significant_digits=-1)

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
        self.assertEqual(ddiff['dic_item_added'],
                         ddiff['dictionary_item_added'])
        self.assertEqual(ddiff['dic_item_removed'],
                         ddiff['dictionary_item_removed'])

    def test_index_and_repeat_dictionary_remapping(self):
        t1 = [1, 3, 1, 4]
        t2 = [4, 4, 1]
        ddiff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True)
        self.assertEqual(ddiff['repetition_change']['root[0]']['newindexes'],
                         ddiff['repetition_change']['root[0]']['new_indexes'])
        self.assertEqual(ddiff['repetition_change']['root[0]']['newrepeat'],
                         ddiff['repetition_change']['root[0]']['new_repeat'])
        self.assertEqual(ddiff['repetition_change']['root[0]']['oldindexes'],
                         ddiff['repetition_change']['root[0]']['old_indexes'])
        self.assertEqual(ddiff['repetition_change']['root[0]']['oldrepeat'],
                         ddiff['repetition_change']['root[0]']['old_repeat'])

    def test_value_and_type_dictionary_remapping(self):
        t1 = {1: 1, 2: 2}
        t2 = {1: 1, 2: '2'}
        ddiff = DeepDiff(t1, t2)
        self.assertEqual(ddiff['type_changes']['root[2]']['newtype'],
                         ddiff['type_changes']['root[2]']['new_type'])
        self.assertEqual(ddiff['type_changes']['root[2]']['newvalue'],
                         ddiff['type_changes']['root[2]']['new_value'])
        self.assertEqual(ddiff['type_changes']['root[2]']['oldtype'],
                         ddiff['type_changes']['root[2]']['old_type'])
        self.assertEqual(ddiff['type_changes']['root[2]']['oldvalue'],
                         ddiff['type_changes']['root[2]']['old_value'])

    def test_skip_type(self):
        l1 = logging.getLogger("test")
        l2 = logging.getLogger("test2")
        t1 = {"log": l1, 2: 1337}
        t2 = {"log": l2, 2: 1337}
        ddiff = DeepDiff(t1, t2, exclude_types={logging.Logger})
        self.assertEqual(ddiff, {})

        t1 = {"log": "book", 2: 1337}
        t2 = {"log": l2, 2: 1337}
        ddiff = DeepDiff(t1, t2, exclude_types={logging.Logger})
        self.assertEqual(ddiff, {})

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
        self.assertEqual(ddiff, {})

    def test_skip_path2(self):
        t1 = {
            "for life": "vegan",
            "ingredients": ["no meat", "no eggs", "no dairy"]
        }
        t2 = {"for life": "vegan"}
        ddiff = DeepDiff(t1, t2, exclude_paths={"root['ingredients']"})
        self.assertEqual(ddiff, {})

    def test_skip_path2_reverse(self):
        t1 = {
            "for life": "vegan",
            "ingredients": ["no meat", "no eggs", "no dairy"]
        }
        t2 = {"for life": "vegan"}
        ddiff = DeepDiff(t2, t1, exclude_paths={"root['ingredients']"})
        self.assertEqual(ddiff, {})

    def test_skip_path4(self):
        t1 = {
            "for life": "vegan",
            "ingredients": ["no meat", "no eggs", "no dairy"]
        }
        t2 = {"for life": "vegan", "zutaten": ["veggies", "tofu", "soy sauce"]}
        ddiff = DeepDiff(t1, t2, exclude_paths={"root['ingredients']"})
        self.assertTrue('dictionary_item_added' in ddiff, {})
        self.assertTrue('dictionary_item_removed' not in ddiff, {})

    def test_skip_custom_object_path(self):
        t1 = CustomClass(1)
        t2 = CustomClass(2)
        ddiff = DeepDiff(t1, t2, exclude_paths=['root.a'])
        result = {}
        self.assertEqual(ddiff, result)

    def test_skip_list_path(self):
        t1 = ['a', 'b']
        t2 = ['a']
        ddiff = DeepDiff(t1, t2, exclude_paths=['root[1]'])
        result = {}
        self.assertEqual(ddiff, result)

    def test_skip_dictionary_path(self):
        t1 = {1: {2: "a"}}
        t2 = {1: {}}
        ddiff = DeepDiff(t1, t2, exclude_paths=['root[1][2]'])
        result = {}
        self.assertEqual(ddiff, result)

    def test_skip_dictionary_path_with_custom_object(self):
        obj1 = CustomClass(1)
        obj2 = CustomClass(2)

        t1 = {1: {2: obj1}}
        t2 = {1: {2: obj2}}
        ddiff = DeepDiff(t1, t2, exclude_paths=['root[1][2].a'])
        result = {}
        self.assertEqual(ddiff, result)

    def test_skip_regexp(self):
        t1 = [{'a': 1, 'b': 2}, {'c': 4, 'b': 5}]
        t2 = [{'a': 1, 'b': 3}, {'c': 4, 'b': 5}]
        ddiff = DeepDiff(t1, t2, exclude_regex_paths=["root\[\d+\]\['b'\]"])
        result = {}
        self.assertEqual(ddiff, result)

    def test_skip_str_type_in_dictionary(self):
        t1 = {1: {2: "a"}}
        t2 = {1: {}}
        ddiff = DeepDiff(t1, t2, exclude_types=[str])
        result = {}
        self.assertEqual(ddiff, result)

    def test_unknown_parameters(self):
        with self.assertRaises(ValueError):
            DeepDiff(1, 1, wrong_param=2)

    def test_bad_attribute(self):
        class Bad(object):
            __slots__ = ['x', 'y']

            def __getattr__(self, key):
                raise AttributeError("Bad item")

            def __str__(self):
                return "Bad Object"

        t1 = Bad()
        t2 = Bad()

        ddiff = DeepDiff(t1, t2)
        result = {'unprocessed': ['root: Bad Object and Bad Object']}
        self.assertEqual(ddiff, result)

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

        self.assertEqual(ddiff, result)

    @mock.patch('deepdiff.diff.logger')
    @mock.patch('deepdiff.diff.DeepHash')
    def test_diff_when_hash_fails(self, mock_DeepHash, mock_logger):
        mock_DeepHash.side_effect = Exception('Boom!')
        t1 = {"blah": {4}, 2: 1337}
        t2 = {"blah": {4}, 2: 1337}
        DeepDiff(t1, t2, ignore_order=True)
        assert mock_logger.warning.called
