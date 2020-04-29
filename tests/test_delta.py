import pytest
from decimal import Decimal
from unittest import mock
from deepdiff import Delta, DeepDiff
from deepdiff.diff import DELTA_VIEW
from deepdiff.helper import get_diff_length, np
from deepdiff.delta import (
    DISABLE_DELTA, DELTA_SKIP_MSG, ELEM_NOT_FOUND_TO_ADD_MSG,
    VERIFICATION_MSG, VERIFY_SYMMETRY_MSG, not_found, DeltaNumpyOperatorOverrideError)

from tests import PicklableClass, parameterize_cases


@pytest.mark.skipif(DISABLE_DELTA, reason=DELTA_SKIP_MSG)
class TestBasicsOfDelta:

    def test_list_difference_add_delta(self):
        t1 = [1, 2]
        t2 = [1, 2, 3, 5]
        diff = {'iterable_item_added': {'root[2]': 3, 'root[3]': 5}}
        delta = Delta(diff)

        assert delta + t1 == t2
        assert t1 + delta == t2

    @mock.patch('deepdiff.delta.logger.error')
    def test_list_difference_add_delta_when_index_not_valid(self, mock_logger):
        t1 = [1, 2]
        diff = {'iterable_item_added': {'root[20]': 3, 'root[3]': 5}}
        delta = Delta(diff, log_errors=False)
        assert delta + t1 == t1

        expected_msg = ELEM_NOT_FOUND_TO_ADD_MSG.format(20, 'root[20]')

        delta2 = Delta(diff, verify_symmetry=True, raise_errors=True, log_errors=False)
        with pytest.raises(ValueError) as excinfo:
            delta2 + t1
        assert expected_msg == str(excinfo.value)
        assert not mock_logger.called

        delta3 = Delta(diff, verify_symmetry=True, raise_errors=True, log_errors=True)
        with pytest.raises(ValueError) as excinfo:
            delta3 + t1
        assert expected_msg == str(excinfo.value)
        mock_logger.assert_called_once_with(expected_msg)

    def test_list_difference3_delta(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 5]}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 3, 2, 5]}}
        diff = {
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
        delta = Delta(diff)

        assert delta + t1 == t2
        assert t1 + delta == t2

    def test_list_difference_delta_raises_error_if_prev_value_does_not_match(self):
        t1 = [1, 2, 6]
        t2 = [1, 3, 2, 5]
        diff = {
            'values_changed': {
                "root[2]": {
                    'new_value': 2,
                    'old_value': 5
                },
                "root[1]": {
                    'new_value': 3,
                    'old_value': 2
                }
            },
            'iterable_item_added': {
                "root[3]": 5
            }
        }

        expected_msg = VERIFICATION_MSG.format('root[2]', 5, 6, VERIFY_SYMMETRY_MSG)

        delta = Delta(diff, verify_symmetry=True, raise_errors=True)
        with pytest.raises(ValueError) as excinfo:
            delta + t1
        assert expected_msg == str(excinfo.value)

        delta2 = Delta(diff, verify_symmetry=False)
        assert delta2 + t1 == t2

    def test_list_difference_delta1(self):
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

        diff = {
            'iterable_item_removed': {
                "root[4]['b'][2]": "to_be_removed",
                "root[4]['b'][3]": 'to_be_removed2'
            }
        }
        delta = Delta(diff)

        assert delta + t1 == t2

    def test_list_difference_delta_if_item_is_already_removed(self):
        t1 = [1, 2, 'to_be_removed']
        t2 = [1, 2]

        diff = {
            'iterable_item_removed': {
                "root[2]": "to_be_removed",
                "root[3]": 'to_be_removed2'
            }
        }
        expected_msg = VERIFICATION_MSG.format("root[3]", 'to_be_removed2', not_found, 'list index out of range')

        delta = Delta(diff, verify_symmetry=True, raise_errors=True)
        with pytest.raises(ValueError) as excinfo:
            delta + t1
        assert expected_msg == str(excinfo.value)

        delta2 = Delta(diff, verify_symmetry=False, raise_errors=True)
        assert t1 + delta2 == t2

    def test_list_difference_delta_raises_error_if_prev_value_changed(self):
        t1 = {
            1: 1,
            2: 2,
            3: 3,
            4: {
                "a": "hello",
                "b": [1, 2, 'wrong', 'to_be_removed2']
            }
        }
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2]}}

        diff = {
            'iterable_item_removed': {
                "root[4]['b'][2]": "to_be_removed",
                "root[4]['b'][3]": 'to_be_removed2'
            }
        }
        expected_msg = VERIFICATION_MSG.format("root[4]['b'][2]", 'to_be_removed', 'wrong', VERIFY_SYMMETRY_MSG)

        delta = Delta(diff, verify_symmetry=True, raise_errors=True)
        with pytest.raises(ValueError) as excinfo:
            delta + t1
        assert expected_msg == str(excinfo.value)

        delta2 = Delta(diff, verify_symmetry=False, raise_errors=True)
        assert t1 + delta2 == t2


picklalbe_obj_without_item = PicklableClass(11)
del picklalbe_obj_without_item.item


DELTA_CASES = {
    'delta_case1': {
        't1': frozenset([1, 2, 'B']),
        't2': frozenset([1, 2, 3, 5]),
        'deepdiff_kwargs': {},
        'to_delta_kwargs': {},
        'expected_delta_dict': {'set_item_removed': {'root': {'B'}}, 'set_item_added': {'root': {3, 5}}},
    },
    'delta_case2': {
        't1': [1, 2, 'B'],
        't2': [1, 2, 3, 5],
        'deepdiff_kwargs': {},
        'to_delta_kwargs': {},
        'expected_delta_dict': {
            'type_changes': {
                'root[2]': {
                    'old_type': str,
                    'new_type': int,
                    'new_value': 3
                }
            },
            'iterable_item_added': {
                'root[3]': 5
            }
        },
    },
    'delta_case3': {
        't1': [1, 2, '3'],
        't2': [1, 2, 3],
        'deepdiff_kwargs': {},
        'to_delta_kwargs': {},
        'expected_delta_dict': {
            'type_changes': {
                'root[2]': {
                    'old_type': str,
                    'new_type': int,
                }
            }
        },
    },
    'delta_case4': {
        't1': 3,
        't2': '3',
        'deepdiff_kwargs': {},
        'to_delta_kwargs': {},
        'expected_delta_dict': {
            'type_changes': {
                'root': {
                    'old_type': int,
                    'new_type': str,
                }
            }
        },
    },
    'delta_case5': {
        't1': 3.2,
        't2': Decimal('3.2'),
        'deepdiff_kwargs': {},
        'to_delta_kwargs': {},
        'expected_delta_dict': {
            'type_changes': {
                'root': {
                    'old_type': float,
                    'new_type': Decimal,
                    'new_value': Decimal('3.2')
                }
            }
        },
    },
    'delta_case6': {
        't1': (1, 2),
        't2': (1, 3),
        'deepdiff_kwargs': {},
        'to_delta_kwargs': {},
        'expected_delta_dict': {
            'values_changed': {
                'root[1]': {
                    'new_value': 3
                }
            }
        },
    },
    'delta_case7': {
        't1': (1, 2, 5),
        't2': (1, ),
        'deepdiff_kwargs': {},
        'to_delta_kwargs': {},
        'expected_delta_dict': {
            'iterable_item_removed': {
                'root[1]': 2,
                'root[2]': 5
            }
        },
    },
    'delta_case8': {
        't1': (1, 2, 5),
        't2': (1, 3),
        'deepdiff_kwargs': {},
        'to_delta_kwargs': {},
        'expected_delta_dict': {
            'iterable_item_removed': {
                'root[2]': 5
            },
            'values_changed': {
                'root[1]': {
                    'new_value': 3
                }
            }
        },
    },
    'delta_case9': {
        't1': (1, ),
        't2': (1, 3),
        'deepdiff_kwargs': {},
        'to_delta_kwargs': {},
        'expected_delta_dict': {
            'iterable_item_added': {
                'root[1]': 3
            },
        },
    },
    'delta_case10': {
        't1': {
            2: 2
        },
        't2': {
            2: 2,
            3: 3
        },
        'deepdiff_kwargs': {},
        'to_delta_kwargs': {},
        'expected_delta_dict': {
            'dictionary_item_added': {
                'root[3]': 3
            },
        },
    },
    'delta_case11': {
        't1': {
            1: 1,
            2: 2
        },
        't2': {
            2: 2,
            3: 3
        },
        'deepdiff_kwargs': {},
        'to_delta_kwargs': {},
        'expected_delta_dict': {
            'dictionary_item_added': {
                'root[3]': 3
            },
            'dictionary_item_removed': {
                'root[1]': 1
            },
        },
    },
    'delta_case12': {
        't1': PicklableClass(10),
        't2': PicklableClass(11),
        'deepdiff_kwargs': {},
        'to_delta_kwargs': {},
        'expected_delta_dict': {
            'values_changed': {
                'root.item': {
                    'new_value': 11
                }
            }
        }
    },
    'delta_case13': {
        't1': PicklableClass(10),
        't2': picklalbe_obj_without_item,
        'deepdiff_kwargs': {},
        'to_delta_kwargs': {},
        'expected_delta_dict': {
            'attribute_removed': {
                'root.item': 10
            }
        }
    },
    'delta_case14': {
        't1': picklalbe_obj_without_item,
        't2': PicklableClass(10),
        'deepdiff_kwargs': {},
        'to_delta_kwargs': {},
        'expected_delta_dict': {
            'attribute_added': {
                'root.item': 10
            }
        }
    },
    'delta_case15_diffing_simple_numbers': {
        't1': 1,
        't2': 2,
        'deepdiff_kwargs': {},
        'to_delta_kwargs': {},
        'expected_delta_dict': {'values_changed': {'root': {'new_value': 2}}}
    },
}


DELTA_CASES_PARAMS = parameterize_cases('t1, t2, deepdiff_kwargs, to_delta_kwargs, expected_delta_dict', DELTA_CASES)


@pytest.mark.skipif(DISABLE_DELTA, reason=DELTA_SKIP_MSG)
class TestDelta:

    @pytest.mark.parametrize(**DELTA_CASES_PARAMS)
    def test_delta_cases(self, t1, t2, deepdiff_kwargs, to_delta_kwargs, expected_delta_dict):
        diff = DeepDiff(t1, t2, **deepdiff_kwargs)
        delta_dict = diff.to_delta_dict(**to_delta_kwargs)
        assert expected_delta_dict == delta_dict
        delta = Delta(diff, verify_symmetry=False, raise_errors=True)
        assert t1 + delta == t2


DELTA_IGNORE_ORDER_CASES = {
    'delta_ignore_order_case1': {
        't1': [1, 2, 'B', 3],
        't2': [1, 2, 3, 5],
        'deepdiff_kwargs': {
            'ignore_order': True,
            'report_repetition': True
        },
        'to_delta_kwargs': {},
        'expected_delta_dict': {
            'iterable_items_added_at_indexes': {
                'root': {
                    3: 5
                }
            },
            'iterable_items_removed_at_indexes': {
                'root': {
                    2: 'B'
                }
            }
        },
        'expected_t1_plus_delta': 't2',
    },
    'delta_ignore_order_case2': {
        't1': [1, 2, 'B', 3, 'B', 'B', 4],
        't2': [1, 2, 3, 5],
        'deepdiff_kwargs': {
            'ignore_order': True,
            'report_repetition': True
        },
        'to_delta_kwargs': {},
        'expected_delta_dict': {
            'iterable_items_added_at_indexes': {
                'root': {
                    3: 5
                }
            },
            'iterable_items_removed_at_indexes': {
                'root': {
                    2: 'B',
                    4: 'B',
                    5: 'B',
                    6: 4
                }
            }
        },
        'expected_t1_plus_delta': 't2',
    },
    'delta_ignore_order_case3': {
        't1': [5, 1, 1, 1, 6],
        't2': [7, 1, 1, 1, 8],
        'deepdiff_kwargs': {
            'ignore_order': True,
            'report_repetition': True
        },
        'to_delta_kwargs': {},
        'expected_delta_dict': {
            'iterable_items_added_at_indexes': {
                'root': {
                    0: 7,
                    4: 8
                }
            },
            'iterable_items_removed_at_indexes': {
                'root': {
                    4: 6,
                    0: 5
                }
            }
        },
        'expected_t1_plus_delta': 't2',
    },
    'delta_ignore_order_case4': {
        't1': [5, 1, 3, 1, 4, 4, 6],
        't2': [7, 4, 4, 1, 3, 4, 8],
        'deepdiff_kwargs': {
            'ignore_order': True,
            'report_repetition': True
        },
        'to_delta_kwargs': {},
        'expected_delta_dict': {
            'iterable_items_added_at_indexes': {
                'root': {
                    0: 7,
                    6: 8,
                    3: 1,
                    1: 4,
                    2: 4,
                    5: 4
                }
            },
            'iterable_items_removed_at_indexes': {
                'root': {
                    6: 6,
                    0: 5
                }
            }
        },
        'expected_t1_plus_delta': 't2',
    },
    'delta_ignore_order_case5': {
        't1': (5, 1, 3, 1, 4, 4, 6),
        't2': (7, 4, 4, 1, 3, 4, 8, 1),
        'deepdiff_kwargs': {
            'ignore_order': True,
            'report_repetition': True
        },
        'to_delta_kwargs': {},
        'expected_delta_dict': {
            'iterable_items_added_at_indexes': {
                'root': {
                    0: 7,
                    6: 8,
                    1: 4,
                    2: 4,
                    5: 4
                }
            },
            'iterable_items_removed_at_indexes': {
                'root': {
                    6: 6,
                    0: 5
                }
            }
        },
        'expected_t1_plus_delta': 't2',
    },
    'delta_ignore_order_case6': {
        't1': [{1, 2, 3}, {4, 5}],
        't2': [{4, 5, 6}, {1, 2, 3}],
        'deepdiff_kwargs': {
            'ignore_order': True,
            'report_repetition': True
        },
        'to_delta_kwargs': {},
        'expected_delta_dict': {'set_item_added': {'root[1]': {6}}},
        'expected_t1_plus_delta': [{1, 2, 3}, {4, 5, 6}],
    },
    'delta_ignore_order_case7': {
        't1': [{1, 2, 3}, {4, 5, 'hello', 'right!'}, {4, 5, (2, 4, 7)}],
        't2': [{4, 5, 6, (2, )}, {1, 2, 3}, {5, 'hello', 'right!'}],
        'deepdiff_kwargs': {
            'ignore_order': True,
            'report_repetition': True
        },
        'to_delta_kwargs': {},
        'expected_delta_dict': {
            'set_item_removed': {
                'root[2]': {(2, 4, 7)},
                'root[1]': {4}
            },
            'set_item_added': {
                'root[2]': {(2, ), 6}
            }
        },
        'expected_t1_plus_delta': [{1, 2, 3}, {'hello', 'right!', 5}, {(2,), 4, 5, 6}],
    },
    'delta_ignore_order_case8_multi_dimensional_list': {
        't1': [[1, 2, 3, 4], [4, 2, 2, 1]],
        't2': [[4, 1, 1, 1], [1, 3, 2, 4]],
        'deepdiff_kwargs': {
            'ignore_order': True,
            'report_repetition': True
        },
        'to_delta_kwargs': {},
        'expected_delta_dict': {
            'iterable_items_added_at_indexes': {
                'root[1]': {
                    1: 1,
                    2: 1,
                    3: 1
                }
            },
            'iterable_items_removed_at_indexes': {
                'root[1]': {
                    1: 2,
                    2: 2
                }
            }
        },
        'expected_t1_plus_delta': [[1, 2, 3, 4], [4, 1, 1, 1]],
    },
}


DELTA_IGNORE_ORDER_CASES_PARAMS = parameterize_cases(
    't1, t2, deepdiff_kwargs, to_delta_kwargs, expected_delta_dict, expected_t1_plus_delta', DELTA_IGNORE_ORDER_CASES)


@pytest.mark.skipif(DISABLE_DELTA, reason=DELTA_SKIP_MSG)
class TestIgnoreOrderDelta:

    @pytest.mark.parametrize(**DELTA_IGNORE_ORDER_CASES_PARAMS)
    def test_ignore_order_delta_cases(
            self, t1, t2, deepdiff_kwargs, to_delta_kwargs, expected_delta_dict, expected_t1_plus_delta):
        diff = DeepDiff(t1, t2, **deepdiff_kwargs)
        delta_dict = diff.to_delta_dict(**to_delta_kwargs)
        assert expected_delta_dict == delta_dict
        delta = Delta(diff, verify_symmetry=False, raise_errors=True)
        expected_t1_plus_delta = t2 if expected_t1_plus_delta == 't2' else expected_t1_plus_delta
        assert t1 + delta == expected_t1_plus_delta


DELTA_NUMPY_TEST_CASES = {
    'delta_case15_similar_to_delta_numpy': {
        't1': [1, 2, 3],
        't2': [1, 2, 5],
        'deepdiff_kwargs': {},
        'to_delta_kwargs': {},
        'expected_delta_dict': {'values_changed': {'root[2]': {'new_value': 5}}},
        'expected_result': 't2'
    },
    'delta_numpy1_operator_override': {
        't1': np.array([1, 2, 3], np.int8),
        't2': np.array([1, 2, 5], np.int8),
        'deepdiff_kwargs': {},
        'to_delta_kwargs': {},
        'expected_delta_dict': {'values_changed': {'root[2]': {'new_value': 5}}, 'numpy_used': True},
        'expected_result': DeltaNumpyOperatorOverrideError
    },
    'delta_numpy2': {
        't1': np.array([1, 2, 3], np.int8),
        't2': np.array([1, 2, 5], np.int8),
        'deepdiff_kwargs': {},
        'to_delta_kwargs': {},
        'expected_delta_dict': {'values_changed': {'root[2]': {'new_value': 5}}, 'numpy_used': True},
        'expected_result': 't2'
    },
    'delta_numpy3_type_change_but_no_value_change': {
        't1': np.array([1, 2, 3], np.int8),
        't2': np.array([1, 2, 3], np.int16),
        'deepdiff_kwargs': {},
        'to_delta_kwargs': {},
        'expected_delta_dict': {'type_changes': {'root': {'old_type': np.int8, 'new_type': np.int16}}},
        'expected_result': 't2'
    },
    'delta_numpy4_type_change_plus_value_change': {
        't1': np.array([1, 2, 3], np.int8),
        't2': np.array([1, 2, 5], np.int16),
        'deepdiff_kwargs': {},
        'to_delta_kwargs': {},
        'expected_delta_dict': None,  # Not easy to compare since it throws:
        # ValueError: The truth value of an array with more than one element is ambiguous.
        # And we don't want to use DeepDiff for testing the equality inside deepdiff tests themselves!
        'expected_result': 't2'
    },
    'delta_numpy4_type_change_ignore_numeric_type_changes': {
        't1': np.array([1, 2, 3], np.int8),
        't2': np.array([1, 2, 5], np.int16),
        'deepdiff_kwargs': {
            'ignore_numeric_type_changes': True
        },
        'to_delta_kwargs': {},
        'expected_delta_dict': {
            'values_changed': {
                'root[2]': {
                    'new_value': 5
                }
            },
            'numpy_used': True
        },
        'expected_result': 't2'
    },
    'delta_numpy5_multi_dimensional': {
        't1': np.array([[1, 2, 3], [4, 2, 2]], np.int8),
        't2': np.array([[1, 2, 5], [4, 1, 2]], np.int8),
        'deepdiff_kwargs': {},
        'to_delta_kwargs': {},
        'expected_delta_dict': {
            'values_changed': {
                'root[0][2]': {
                    'new_value': 5
                },
                'root[1][1]': {
                    'new_value': 1
                }
            },
            'numpy_used': True
        },
        'expected_result': 't2'
    },
    'delta_numpy6_multi_dimensional_ignore_order': {
        't1': np.array([[1, 2, 3, 4], [4, 2, 2, 1]], np.int8),
        't2': np.array([[4, 1, 1, 1], [1, 3, 2, 4]], np.int8),
        'deepdiff_kwargs': {
            'ignore_order': True,
            'report_repetition': True
        },
        'to_delta_kwargs': {},
        'expected_delta_dict': {
            'iterable_items_added_at_indexes': {
                'root[1]': {
                    1: 1,
                    2: 1,
                    3: 1
                }
            },
            'iterable_items_removed_at_indexes': {
                'root[1]': {
                    1: 2,
                    2: 2
                }
            },
            'numpy_used': True
        },
        'expected_result': 't2_via_deepdiff'
    },
}

DELTA_NUMPY_TEST_PARAMS = parameterize_cases(
    't1, t2, deepdiff_kwargs, to_delta_kwargs, expected_delta_dict, expected_result', DELTA_NUMPY_TEST_CASES)


@pytest.mark.skipif(DISABLE_DELTA, reason=DELTA_SKIP_MSG)
class TestNumpyDelta:

    @pytest.mark.parametrize(**DELTA_NUMPY_TEST_PARAMS)
    def test_numpy_delta_cases(self, t1, t2, deepdiff_kwargs, to_delta_kwargs, expected_delta_dict, expected_result):
        diff = DeepDiff(t1, t2, **deepdiff_kwargs)
        delta_dict = diff.to_delta_dict(**to_delta_kwargs)
        if expected_delta_dict:
            assert expected_delta_dict == delta_dict
        delta = Delta(diff, verify_symmetry=False, raise_errors=True)
        if expected_result == 't2':
            result = delta + t1
            assert np.array_equal(result, t2)
        elif expected_result == 't2_via_deepdiff':
            result = delta + t1
            diff = DeepDiff(result, t2, ignore_order=True, report_repetition=True)
            assert not diff
        elif expected_result is DeltaNumpyOperatorOverrideError:
            with pytest.raises(DeltaNumpyOperatorOverrideError):
                assert t1 + delta
        else:
            result = delta + t1
            assert np.array_equal(result, expected_result)


class TestDiffLength:

    @pytest.mark.parametrize('diff, expected_length', [
        (
            {'set_item_added': {'root[1]': {6}}},
            1
        ),
        (
            {
                'iterable_items_added_at_indexes': {
                    'root': {
                        0: 7,
                        6: 8,
                        1: 4,
                        2: 4,
                        5: 4
                    }
                },
                'iterable_items_removed_at_indexes': {
                    'root': {
                        6: 6,
                        0: 5
                    }
                }
            },
            7
        ),
        (
            {
                'type_changes': {
                    'root': {
                        'old_type': float,
                        'new_type': Decimal,
                        'new_value': Decimal('3.2')
                    }
                }
            },
            3
        ),
    ])
    def test_diff_length(self, diff, expected_length):
        length = get_diff_length(diff)
        assert expected_length == length


class TestDeltaView:

    def test_delta_view_of_the_same_objects(self):
        t1 = [{1, 2, 3}, {4, 5, 6}]
        t2 = [{4, 5, 6}, {1, 2, 3}]
        ddiff = DeepDiff(t1, t2, ignore_order=True, view=DELTA_VIEW)
        assert {} == ddiff
        assert 0 == get_diff_length(ddiff)
        assert '0' == str(ddiff.get_rough_distance())[:10]
        assert 9 == ddiff._DeepDiff__get_item_rough_length(ddiff.t1)
        assert 9 == ddiff._DeepDiff__get_item_rough_length(ddiff.t2)

    def test_delta_view_of_list_sets(self):
        t1 = [{1, 2, 3}, {4, 5}]
        t2 = [{4, 5, 6}, {1, 2, 3}]
        ddiff = DeepDiff(t1, t2, ignore_order=True, view=DELTA_VIEW)
        assert {'set_item_added': {'root[1]': {6}}} == ddiff
        assert 1 == get_diff_length(ddiff)
        assert '0.05882352' == str(ddiff.get_rough_distance())[:10]
        assert 8 == ddiff._DeepDiff__get_item_rough_length(ddiff.t1)
        assert 9 == ddiff._DeepDiff__get_item_rough_length(ddiff.t2)

    def test_delta_view_of_list_sets2(self):
        t1 = [{1, 2, 3}, {4, 5}, {1}]
        t2 = [{4, 5, 6}, {1, 2, 3}, {1, 4}]
        ddiff = DeepDiff(t1, t2, ignore_order=True, view=DELTA_VIEW)
        assert {'set_item_added': {'root[2]': {4}, 'root[1]': {6}}} == ddiff
        assert 2 == get_diff_length(ddiff)
        assert '0.09090909' == str(ddiff.get_rough_distance())[:10]
        assert 10 == ddiff._DeepDiff__get_item_rough_length(ddiff.t1)
        assert 12 == ddiff._DeepDiff__get_item_rough_length(ddiff.t2)

    def test_delta_view_of_list_sets_and_strings(self):
        t1 = [{1, 2, 3}, {4, 5, 'hello', 'right!'}, {4, 5, (2, 4, 7)}]
        t2 = [{4, 5, 6, (2, )}, {1, 2, 3}, {5, 'hello', 'right!'}]
        ddiff = DeepDiff(t1, t2, ignore_order=True, view=DELTA_VIEW)
        expected = {
            'set_item_removed': {
                'root[2]': {(2, 4, 7)},
                'root[1]': {4}
            },
            'set_item_added': {
                'root[2]': {(2, ), 6}
            }
        }
        assert expected == ddiff
        assert 6 == get_diff_length(ddiff)
