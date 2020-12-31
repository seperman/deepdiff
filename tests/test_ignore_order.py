import pytest
from unittest import mock
from deepdiff.helper import number_to_string
from deepdiff import DeepDiff
from decimal import Decimal
from deepdiff.deephash import sha256hex
from tests import CustomClass2


class TestIgnoreOrder:

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

    def test_ignore_order_depth1(self):
        t1 = [{1, 2, 3}, {4, 5}]
        t2 = [{4, 5, 6}, {1, 2, 3}]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        assert {'set_item_added': ["root[1][6]"]} == ddiff

    def test_ignore_order_depth2(self):
        t1 = [[1, 2, 3], [4, 5]]
        t2 = [[4, 5, 6], [1, 2, 3]]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        assert {'iterable_item_added': {'root[1][2]': 6}} == ddiff

    def test_ignore_order_depth3(self):
        t1 = [{1, 2, 3}, [{4, 5}]]
        t2 = [[{4, 5, 6}], {1, 2, 3}]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        assert {'set_item_added': ["root[1][0][6]"]} == ddiff

    def test_ignore_order_depth4(self):
        t1 = [[1, 2, 3, 4], [4, 2, 2, 1]]
        t2 = [[4, 1, 1, 1], [1, 3, 2, 4]]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        assert {'iterable_item_removed': {'root[1][1]': 2}} == ddiff

    def test_ignore_order_depth5(self):
        t1 = [4, 2, 2, 1]
        t2 = [4, 1, 1, 1]
        ddiff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True, cache_purge_level=0)
        expected = {
            'iterable_item_removed': {
                'root[1]': 2,
                'root[2]': 2
            },
            'repetition_change': {
                'root[3]': {
                    'old_repeat': 1,
                    'new_repeat': 3,
                    'old_indexes': [3],
                    'new_indexes': [1, 2, 3],
                    'value': 1
                }
            }
        }
        assert expected == ddiff

        ddiff = DeepDiff(t1, t2, ignore_order=True, report_repetition=False, cache_purge_level=0)
        dist = ddiff._get_rough_distance()
        assert 0.1 == dist

    def test_ignore_order_depth6(self):
        t1 = [[1, 2, 3, 4], [4, 2, 2, 1]]
        t2 = [[4, 1, 1, 1], [1, 3, 2, 4]]
        ddiff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True)
        expected = {
            'iterable_item_removed': {
                'root[1][1]': 2,
                'root[1][2]': 2
            },
            'repetition_change': {
                'root[1][3]': {
                    'old_repeat': 1,
                    'new_repeat': 3,
                    'old_indexes': [3],
                    'new_indexes': [1, 2, 3],
                    'value': 1
                }
            }
        }

        assert expected == ddiff

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
        result = {'values_changed': {'root[0]': {'new_value': t2_0, 'old_value': t1_0}}}
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
            'values_changed': {
                'root[1]': {
                    'new_value': {
                        1: 1
                    },
                    'old_value': {
                        'a': 2
                    }
                }
            },
            'iterable_item_removed': {
                'root[0]': 1,
                'root[4]': 'B'
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

    def test_list_ignore_order_report_repetition(self):
        t1 = [5, 1, 3, 1, 4, 4, 6]
        t2 = [7, 4, 4, 1, 3, 4, 8]
        ddiff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True)
        result = {
            'values_changed': {
                'root[6]': {
                    'new_value': 7,
                    'old_value': 6
                },
                'root[0]': {
                    'new_value': 8,
                    'old_value': 5
                }
            },
            'repetition_change': {
                'root[4]': {
                    'old_repeat': 2,
                    'new_repeat': 3,
                    'old_indexes': [4, 5],
                    'new_indexes': [1, 2, 5],
                    'value': 4
                },
                'root[1]': {
                    'old_repeat': 2,
                    'new_repeat': 1,
                    'old_indexes': [1, 3],
                    'new_indexes': [3],
                    'value': 1
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
        assert {'values_changed': {"root['key2'][1]['key5']": {'new_value': 'CHANGE', 'old_value': 'val5'}}} == ddiff

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

    def test_custom_objects2(self):
        cc_a = CustomClass2(prop1=["a"], prop2=["b"])
        cc_b = CustomClass2(prop1=["b"], prop2=["b"])
        t1 = [cc_a, CustomClass2(prop1=["c"], prop2=["d"])]
        t2 = [cc_b, CustomClass2(prop1=["c"], prop2=["d"])]

        ddiff = DeepDiff(t1, t2, ignore_order=True)

        result = {'values_changed': {'root[0].prop1[0]': {'new_value': 'b', 'old_value': 'a'}}}
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

    def test_decimal_ignore_order(self):
        t1 = [{1: Decimal('10.1')}, {2: Decimal('10.2')}]
        t2 = [{2: Decimal('10.2')}, {1: Decimal('10.1')}]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        result = {}
        assert result == ddiff

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

    def test_ignore_type_in_groups_numbers_and_strings_when_ignore_order(self):
        t1 = [1, 2, 3, 'a']
        t2 = [1.0, 2.0, 3.3, b'a']
        ddiff = DeepDiff(t1, t2, ignore_numeric_type_changes=True, ignore_string_type_changes=True, ignore_order=True)
        result = {'values_changed': {'root[2]': {'new_value': 3.3, 'old_value': 3}}}
        assert result == ddiff

    def test_ignore_string_type_changes_when_dict_keys_merge_is_not_deterministic(self):
        t1 = {'a': 10, b'a': 20}
        t2 = {'a': 11, b'a': 22}
        ddiff = DeepDiff(t1, t2, ignore_numeric_type_changes=True, ignore_string_type_changes=True, ignore_order=True)
        result = {'values_changed': {"root['a']": {'new_value': 22, 'old_value': 20}}}
        alternative_result = {'values_changed': {"root['a']": {'new_value': 11, 'old_value': 10}}}
        assert result == ddiff or alternative_result == ddiff

    def test_skip_exclude_path5(self):
        exclude_paths = ["root[0]['e']", "root[1]['e']"]

        t1 = [{'a': 1, 'b': 'randomString', 'e': "1111"}]
        t2 = [{'a': 1, 'b': 'randomString', 'e': "2222"}]

        ddiff = DeepDiff(t1, t2, exclude_paths=exclude_paths,
                         ignore_order=True, report_repetition=False)
        result = {}
        assert result == ddiff

    def test_skip_str_type_in_dict_on_list_when_ignored_order(self):
        t1 = [{1: "a"}]
        t2 = [{}]
        ddiff = DeepDiff(t1, t2, exclude_types=[str], ignore_order=True)
        result = {}
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

        ddiff = DeepDiff(t1, t2, ignore_order=True, cutoff_intersection_for_pairs=1)
        assert ddiff == {}

    @pytest.mark.parametrize('max_passes, expected', [
        (0, {'values_changed': {'root[0]': {'new_value': {'key5': 'CHANGE', 'key6': 'val6'}, 'old_value': {'key3': [[[[[1, 2, 4, 5]]]]], 'key4': [7, 8]}}, 'root[1]': {'new_value': {'key3': [[[[[1, 3, 5, 4]]]]], 'key4': [7, 8]}, 'old_value': {'key5': 'val5', 'key6': 'val6'}}}}),
        (1, {'values_changed': {"root[1]['key5']": {'new_value': 'CHANGE', 'old_value': 'val5'}, "root[0]['key3'][0]": {'new_value': [[[[1, 3, 5, 4]]]], 'old_value': [[[[1, 2, 4, 5]]]]}}}),
        (22, {'values_changed': {"root[1]['key5']": {'new_value': 'CHANGE', 'old_value': 'val5'}, "root[0]['key3'][0][0][0][0][1]": {'new_value': 3, 'old_value': 2}}})
    ])
    def test_ignore_order_max_passes(self, max_passes, expected):
        t1 = [
            {
                'key3': [[[[[1, 2, 4, 5]]]]],
                'key4': [7, 8],
            },
            {
                'key5': 'val5',
                'key6': 'val6',
            },
        ]

        t2 = [
            {
                'key5': 'CHANGE',
                'key6': 'val6',
            },
            {
                'key3': [[[[[1, 3, 5, 4]]]]],
                'key4': [7, 8],
            },
        ]

        ddiff = DeepDiff(t1, t2, ignore_order=True, max_passes=max_passes, verbose_level=2, cache_size=5000, cutoff_intersection_for_pairs=1)
        assert expected == ddiff

    @pytest.mark.parametrize('max_diffs, expected', [
        (1, {}),
        (65, {'values_changed': {"root[1]['key5']": {'new_value': 'CHANGE', 'old_value': 'val5'}}}),
        (80, {'values_changed': {"root[1]['key5']": {'new_value': 'CHANGE', 'old_value': 'val5'}, "root[0]['key3'][0][0][0][0][1]": {'new_value': 3, 'old_value': 2}}}),
    ])
    def test_ignore_order_max_diffs(self, max_diffs, expected):
        t1 = [
            {
                'key3': [[[[[1, 2, 4, 5]]]]],
                'key4': [7, 8],
            },
            {
                'key5': 'val5',
                'key6': 'val6',
            },
        ]

        t2 = [
            {
                'key5': 'CHANGE',
                'key6': 'val6',
            },
            {
                'key3': [[[[[1, 3, 5, 4]]]]],
                'key4': [7, 8],
            },
        ]

        # Note: these tests are not exactly deterministic
        ddiff = DeepDiff(t1, t2, ignore_order=True, max_diffs=max_diffs, verbose_level=2, cache_size=5000, cutoff_intersection_for_pairs=1)
        assert expected == ddiff

    def test_stats_that_include_distance_cache_hits(self):
        t1 = [
            [1, 2, 3, 9], [9, 8, 5, 9]
        ]

        t2 = [
            [1, 2, 4, 10], [4, 2, 5]
        ]

        diff = DeepDiff(t1, t2, ignore_order=True, cache_size=5000, cutoff_intersection_for_pairs=1)
        expected = {
            'PASSES COUNT': 7,
            'DIFF COUNT': 37,
            'DISTANCE CACHE HIT COUNT': 0,
            'MAX PASS LIMIT REACHED': False,
            'MAX DIFF LIMIT REACHED': False,
        }
        assert expected == diff.get_stats()

    def test_ignore_order_report_repetition_and_self_loop(self):
        t1 = [[1, 2, 1, 3]]
        t1.append(t1)

        t2 = [[1, 2, 2, 2, 4]]
        t2.append(t2)

        diff = DeepDiff(t1, t2, ignore_order=True, cutoff_intersection_for_pairs=1)
        expected = {
            'values_changed': {
                'root[0][3]': {
                    'new_value': 4,
                    'old_value': 3
                },
                'root[1]': {
                    'new_value': t2,
                    'old_value': t1
                }
            }
        }
        assert expected == diff

        diff2 = DeepDiff(t1, t2, ignore_order=True, cache_size=5000, cutoff_intersection_for_pairs=1)
        assert expected == diff2

    def test_ignore_order_with_sha256_hash(self):
        t1 = [
            [1, 2, 3, 9], [9, 8, 5, 9]
        ]

        t2 = [
            [1, 2, 3, 10], [8, 2, 5]
        ]
        diff = DeepDiff(t1, t2, ignore_order=True, hasher=sha256hex, cutoff_intersection_for_pairs=1)
        expected = {
            'values_changed': {
                'root[0][3]': {
                    'new_value': 10,
                    'old_value': 9
                },
                'root[1][0]': {
                    'new_value': 2,
                    'old_value': 9
                }
            }
        }
        assert expected == diff

    def test_ignore_order_cache_for_individual_distances(self):
        t1 = [[1, 2, 'B', 3], 'B']
        t2 = [[1, 2, 3, 5], 5]
        diff = DeepDiff(t1, t2, ignore_order=True, cache_size=5000, cutoff_intersection_for_pairs=1)
        expected = {
            'values_changed': {
                'root[1]': {
                    'new_value': 5,
                    'old_value': 'B'
                }
            },
            'iterable_item_added': {
                'root[0][3]': 5
            },
            'iterable_item_removed': {
                'root[0][2]': 'B'
            }
        }
        assert expected == diff

        stats = diff.get_stats()
        expected_stats = {
            'PASSES COUNT': 3,
            'DIFF COUNT': 13,
            'DISTANCE CACHE HIT COUNT': 1,
            'MAX PASS LIMIT REACHED': False,
            'MAX DIFF LIMIT REACHED': False
        }
        assert expected_stats == stats

        t1 = [[1, 2, 'B', 3], 5]
        t2 = [[1, 2, 3, 5], 'B']
        diff2 = DeepDiff(t1, t2, ignore_order=True, cache_size=5000, cutoff_intersection_for_pairs=1)
        assert expected_stats == diff2.get_stats()

    def test_cutoff_distance_for_pairs(self):
        t1 = [[1.0]]
        t2 = [[20.0]]
        diff1 = DeepDiff(t1, t2, ignore_order=True, cutoff_distance_for_pairs=0.3)
        expected1 = {'values_changed': {'root[0][0]': {'new_value': 20.0, 'old_value': 1.0}}}
        assert expected1 == diff1

        diff2 = DeepDiff(t1, t2, ignore_order=True, cutoff_distance_for_pairs=0.1)
        expected2 = {'values_changed': {'root[0]': {'new_value': [20.0], 'old_value': [1.0]}}}
        assert expected2 == diff2

        diff_with_dist = DeepDiff(1.0, 20.0, get_deep_distance=True)
        expected = {'values_changed': {'root': {'new_value': 20.0, 'old_value': 1.0}}, 'deep_distance': 0.2714285714285714}

        assert expected == diff_with_dist

    def test_ignore_order_and_group_by(self):
        t1 = [
            {'id': 'AA', 'name': 'Joe', 'ate': ['Nothing']},
            {'id': 'BB', 'name': 'James', 'ate': ['Chips', 'Cheese']},
            {'id': 'CC', 'name': 'Mike', 'ate': ['Apple']},
        ]

        t2 = [
            {'id': 'BB', 'name': 'James', 'ate': ['Chips', 'Brownies', 'Cheese']},
            {'id': 'AA', 'name': 'Joe', 'ate': ['Nothing']},
            {'id': 'CC', 'name': 'Mike', 'ate': ['Apple', 'Apple']},
        ]

        diff = DeepDiff(t1, t2, group_by='id', ignore_order=False)
        expected = {
            'values_changed': {
                "root['BB']['ate'][1]": {
                    'new_value': 'Brownies',
                    'old_value': 'Cheese'
                }
            },
            'iterable_item_added': {
                "root['CC']['ate'][1]": 'Apple',
                "root['BB']['ate'][2]": 'Cheese'
            }
        }
        assert expected == diff

        diff2 = DeepDiff(t1, t2, group_by='id', ignore_order=True)
        expected2 = {'iterable_item_added': {"root['BB']['ate'][1]": 'Brownies'}}
        assert expected2 == diff2
