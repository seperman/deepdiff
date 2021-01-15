import pytest
import os
import io
import json
from decimal import Decimal
from unittest import mock
from deepdiff import Delta, DeepDiff
from deepdiff.helper import np, number_to_string, TEXT_VIEW, DELTA_VIEW
from deepdiff.path import GETATTR, GET
from deepdiff.delta import (
    ELEM_NOT_FOUND_TO_ADD_MSG,
    VERIFICATION_MSG, VERIFY_SYMMETRY_MSG, not_found, DeltaNumpyOperatorOverrideError,
    BINIARY_MODE_NEEDED_MSG, DELTA_AT_LEAST_ONE_ARG_NEEDED, DeltaError,
    INVALID_ACTION_WHEN_CALLING_GET_ELEM, INVALID_ACTION_WHEN_CALLING_SIMPLE_SET_ELEM,
    INVALID_ACTION_WHEN_CALLING_SIMPLE_DELETE_ELEM, INDEXES_NOT_FOUND_WHEN_IGNORE_ORDER,
    FAIL_TO_REMOVE_ITEM_IGNORE_ORDER_MSG, UNABLE_TO_GET_PATH_MSG, NOT_VALID_NUMPY_TYPE)
from deepdiff.serialization import (
    DELTA_IGNORE_ORDER_NEEDS_REPETITION_REPORT, DELTA_ERROR_WHEN_GROUP_BY
)

from tests import PicklableClass, parameterize_cases, CustomClass, CustomClass2


class TestBasicsOfDelta:

    def test_list_difference_add_delta(self):
        t1 = [1, 2]
        t2 = [1, 2, 3, 5]
        diff = {'iterable_item_added': {'root[3]': 5, 'root[2]': 3}}
        delta = Delta(diff)

        assert delta + t1 == t2
        assert t1 + delta == t2

    def test_list_difference_dump_delta(self):
        t1 = [1, 2]
        t2 = [1, 2, 3, 5]
        diff = DeepDiff(t1, t2)
        dump = Delta(diff).dumps()
        delta = Delta(dump)

        assert delta + t1 == t2

    def test_multiple_delta(self):
        t1 = [1, 2]
        t2 = [1, 2, 3, 5]
        t3 = [{1}, 3, 5]
        dump1 = Delta(DeepDiff(t1, t2)).dumps()
        dump2 = Delta(DeepDiff(t2, t3)).dumps()

        delta1 = Delta(dump1)
        delta2 = Delta(dump2)

        assert t1 + delta1 + delta2 == t3

    def test_delta_dump_and_read1(self):
        t1 = [1, 2]
        t2 = [1, 2, 3, 5]
        diff = DeepDiff(t1, t2)
        path = '/tmp/delta_test.delta'
        with open(path, 'wb') as the_file:
            Delta(diff).dump(the_file)
        delta = Delta(delta_path=path)
        os.remove(path)
        assert delta + t1 == t2

    def test_delta_dump_and_read2(self):
        t1 = [1, 2]
        t2 = [1, 2, 3, 5]
        diff = DeepDiff(t1, t2)
        delta_content = Delta(diff).dumps()
        path = '/tmp/delta_test2.delta'
        with open(path, 'wb') as the_file:
            the_file.write(delta_content)
        delta = Delta(delta_path=path)
        os.remove(path)
        assert delta + t1 == t2

    def test_delta_dump_and_read3(self):
        t1 = [1, 2]
        t2 = [1, 2, 3, 5]
        diff = DeepDiff(t1, t2)
        delta_content = Delta(diff).dumps()
        path = '/tmp/delta_test2.delta'
        with open(path, 'wb') as the_file:
            the_file.write(delta_content)
        with pytest.raises(ValueError) as excinfo:
            with open(path, 'r') as the_file:
                delta = Delta(delta_file=the_file)
        assert BINIARY_MODE_NEEDED_MSG[:20] == str(excinfo.value)[:20]
        with open(path, 'rb') as the_file:
            delta = Delta(delta_file=the_file)
        os.remove(path)
        assert delta + t1 == t2

    def test_delta_when_no_arg_passed(self):
        with pytest.raises(ValueError) as excinfo:
            Delta()
        assert DELTA_AT_LEAST_ONE_ARG_NEEDED == str(excinfo.value)

    def test_delta_when_group_by(self):

        t1 = [
            {'id': 'AA', 'name': 'Joe', 'last_name': 'Nobody'},
            {'id': 'BB', 'name': 'James', 'last_name': 'Blue'},
        ]

        t2 = [
            {'id': 'AA', 'name': 'Joe', 'last_name': 'Nobody'},
            {'id': 'BB', 'name': 'James', 'last_name': 'Brown'},
        ]

        diff = DeepDiff(t1, t2, group_by='id')

        with pytest.raises(ValueError) as excinfo:
            Delta(diff)
        assert DELTA_ERROR_WHEN_GROUP_BY == str(excinfo.value)

    def test_delta_repr(self):
        t1 = [1, 2]
        t2 = [1, 2, 3, 5]
        diff = DeepDiff(t1, t2)
        delta = Delta(diff)
        options = {
            "<Delta: {'iterable_item_added': {'root[2]': 3, 'root[3]': 5}}>",
            "<Delta: {'iterable_item_added': {'root[3]': 5, 'root[2]': 3}}>"}
        assert repr(delta) in options

    def test_get_elem_and_compare_to_old_value(self):
        delta = Delta({})

        with pytest.raises(DeltaError) as excinfo:
            delta._get_elem_and_compare_to_old_value(
                obj=None, path_for_err_reporting=None, expected_old_value=None, action='ketchup on steak')
        assert INVALID_ACTION_WHEN_CALLING_GET_ELEM.format('ketchup on steak') == str(excinfo.value)

    def test_simple_set_elem_value(self):
        delta = Delta({}, raise_errors=True)

        with pytest.raises(DeltaError) as excinfo:
            delta._simple_set_elem_value(
                obj=None, elem=None, value=None, action='mayo on salad', path_for_err_reporting=None)
        assert INVALID_ACTION_WHEN_CALLING_SIMPLE_SET_ELEM.format('mayo on salad') == str(excinfo.value)

        with pytest.raises(DeltaError) as excinfo:
            delta._simple_set_elem_value(
                obj={}, elem={1}, value=None, action=GET, path_for_err_reporting='mypath')
        assert str(excinfo.value) in {"Failed to set mypath due to unhashable type: 'set'",
                                      "Failed to set mypath due to 'set' objects are unhashable"}

    def test_simple_delete_elem(self):
        delta = Delta({}, raise_errors=True)

        with pytest.raises(DeltaError) as excinfo:
            delta._simple_delete_elem(
                obj=None, elem=None, action='burnt oil', path_for_err_reporting=None)
        assert INVALID_ACTION_WHEN_CALLING_SIMPLE_DELETE_ELEM.format('burnt oil') == str(excinfo.value)

        with pytest.raises(DeltaError) as excinfo:
            delta._simple_delete_elem(
                obj={}, elem=1, action=GET, path_for_err_reporting='mypath')
        assert "Failed to set mypath due to 1" == str(excinfo.value)

    def test_raise_error(self):
        t1 = [1, 2, [3, 5, 6]]
        t2 = [2, 3, [3, 6, 8]]
        diff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True)
        delta = Delta(diff, raise_errors=False)
        t3 = [1, 2, 3, 5]
        t4 = t3 + delta
        assert [3, 2, 3, 5] == t4

        delta2 = Delta(diff, raise_errors=True)

        with pytest.raises(DeltaError) as excinfo:
            t3 + delta2
        assert "Unable to get the item at root[2][1]" == str(excinfo.value)

    def test_identical_delta(self):
        delta = Delta({})

        t1 = [1, 3]
        assert t1 + delta == t1

    def test_delta_mutate(self):
        t1 = [1, 2]
        t2 = [1, 2, 3, 5]
        diff = DeepDiff(t1, t2)
        delta = Delta(diff, mutate=True)
        t1 + delta
        assert t1 == t2

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

    @mock.patch('deepdiff.delta.logger.error')
    def test_list_difference_delta_if_item_is_already_removed(self, mock_logger):
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
        with pytest.raises(DeltaError) as excinfo:
            delta + t1
        assert expected_msg == str(excinfo.value)

        delta2 = Delta(diff, verify_symmetry=False, raise_errors=False)
        assert t1 + delta2 == t2
        expected_msg = UNABLE_TO_GET_PATH_MSG.format('root[3]')
        mock_logger.assert_called_with(expected_msg)

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
    'delta_case0': {
        't1': frozenset([1, 2, 'B']),
        't2': frozenset([1, 2, 'B']),
        'deepdiff_kwargs': {},
        'to_delta_kwargs': {},
        'expected_delta_dict': {},
    },
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
    'delta_case16_diffmultiline_text': {
        't1': {1: 1, 2: 2, 3: 3, 4: {'a': 'hello', 'b': 'world\n1\n2\nEnd'}},
        't2': {1: 1, 2: 2, 3: 3, 4: {'a': 'hello', 'b': 'world!\nGoodbye!\n1\n2\nEnd'}},
        'deepdiff_kwargs': {},
        'to_delta_kwargs': {},
        'expected_delta_dict': {'values_changed': {"root[4]['b']": {'new_value': 'world!\nGoodbye!\n1\n2\nEnd'}}}
    },
}


DELTA_CASES_PARAMS = parameterize_cases('t1, t2, deepdiff_kwargs, to_delta_kwargs, expected_delta_dict', DELTA_CASES)


class TestDelta:

    @pytest.mark.parametrize(**DELTA_CASES_PARAMS)
    def test_delta_cases(self, t1, t2, deepdiff_kwargs, to_delta_kwargs, expected_delta_dict):
        diff = DeepDiff(t1, t2, **deepdiff_kwargs)
        delta_dict = diff._to_delta_dict(**to_delta_kwargs)
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
            'values_changed': {
                'root[6]': {
                    'new_value': 5
                }
            },
            'iterable_items_removed_at_indexes': {
                'root': {
                    2: 'B',
                    4: 'B',
                    5: 'B'
                }
            }
        },
        'expected_t1_plus_delta': 't2',
    },
    'delta_ignore_order_case_reverse2': {
        't1': [1, 2, 3, 5],
        't2': [1, 2, 'B', 3, 'B', 'B', 4],
        'deepdiff_kwargs': {
            'ignore_order': True,
            'report_repetition': True
        },
        'to_delta_kwargs': {},
        'expected_delta_dict': {
            'values_changed': {
                'root[3]': {
                    'new_value': 4
                }
            },
            'iterable_items_added_at_indexes': {
                'root': {
                    2: 'B',
                    4: 'B',
                    5: 'B'
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
            'values_changed': {
                'root[4]': {
                    'new_value': 7
                },
                'root[0]': {
                    'new_value': 8
                }
            }
        },
        'expected_t1_plus_delta': [8, 1, 1, 1, 7],
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
            'values_changed': {
                'root[6]': {
                    'new_value': 7
                },
                'root[0]': {
                    'new_value': 8
                }
            },
            'iterable_items_added_at_indexes': {
                'root': {
                    1: 4,
                    2: 4,
                    5: 4,
                    3: 1,
                }
            }
        },
        'expected_t1_plus_delta': [8, 4, 4, 1, 3, 4, 7],
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
                    1: 4,
                    2: 4,
                    5: 4
                }
            },
            'values_changed': {
                'root[6]': {
                    'new_value': 7
                },
                'root[0]': {
                    'new_value': 8
                }
            }
        },
        'expected_t1_plus_delta': (8, 4, 4, 1, 3, 4, 1, 7),
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
                'root[1]': {4}
            },
            'iterable_items_added_at_indexes': {
                'root': {
                    0: {(2, ), 4, 5, 6}
                }
            },
            'iterable_items_removed_at_indexes': {
                'root': {
                    2: {4, 5, (2, 4, 7)}
                }
            }
        },
        'expected_t1_plus_delta': 't2',
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


class TestIgnoreOrderDelta:

    @pytest.mark.parametrize(**DELTA_IGNORE_ORDER_CASES_PARAMS)
    def test_ignore_order_delta_cases(
            self, t1, t2, deepdiff_kwargs, to_delta_kwargs, expected_delta_dict, expected_t1_plus_delta):
        diff = DeepDiff(t1, t2, **deepdiff_kwargs)
        delta_dict = diff._to_delta_dict(**to_delta_kwargs)
        assert expected_delta_dict == delta_dict
        delta = Delta(diff, verify_symmetry=False, raise_errors=True)
        expected_t1_plus_delta = t2 if expected_t1_plus_delta == 't2' else expected_t1_plus_delta
        t1_plus_delta = t1 + delta
        assert t1_plus_delta == expected_t1_plus_delta
        assert t1 + delta == t1_plus_delta  # asserting that delta is not mutated once it is applied.


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
        'expected_delta_dict': {'values_changed': {'root[2]': {'new_value': 5}}, '_numpy_paths': {'root': 'int8'}},
        'expected_result': DeltaNumpyOperatorOverrideError
    },
    'delta_numpy2': {
        't1': np.array([1, 2, 3], np.int8),
        't2': np.array([1, 2, 5], np.int8),
        'deepdiff_kwargs': {},
        'to_delta_kwargs': {},
        'expected_delta_dict': {'values_changed': {'root[2]': {'new_value': 5}}, '_numpy_paths': {'root': 'int8'}},
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
            '_numpy_paths': {
                'root': 'int16'
            }
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
            '_numpy_paths': {
                'root': 'int8'
            }
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
            '_numpy_paths': {
                'root': 'int8'
            }
        },
        'expected_result': 't2_via_deepdiff'
    },
    'delta_numpy7_arrays_of_different_sizes': {
        't1': np.array([1, 2, 3, 4]),
        't2': np.array([5, 6, 7, 8, 9, 10]),
        'deepdiff_kwargs': {},
        'to_delta_kwargs': {},
        'expected_delta_dict': {
            'values_changed': {
                'root[0]': {
                    'new_value': 5
                },
                'root[1]': {
                    'new_value': 6
                },
                'root[2]': {
                    'new_value': 7
                },
                'root[3]': {
                    'new_value': 8
                }
            },
            'iterable_item_added': {
                'root[4]': 9,
                'root[5]': 10
            },
            '_numpy_paths': {
                'root': 'int64'
            }
        },
        'expected_result': 't2'
    },
}


DELTA_NUMPY_TEST_PARAMS = parameterize_cases(
    't1, t2, deepdiff_kwargs, to_delta_kwargs, expected_delta_dict, expected_result', DELTA_NUMPY_TEST_CASES)


class TestNumpyDelta:

    @pytest.mark.parametrize(**DELTA_NUMPY_TEST_PARAMS)
    def test_numpy_delta_cases(self, t1, t2, deepdiff_kwargs, to_delta_kwargs, expected_delta_dict, expected_result):
        diff = DeepDiff(t1, t2, **deepdiff_kwargs)
        delta_dict = diff._to_delta_dict(**to_delta_kwargs)
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

    def test_invalid_numpy_type(self):

        t1 = np.array([1, 2, 3], np.int8)
        delta_dict = {'iterable_item_added': {'root[2]': 5}, '_numpy_paths': {'root': 'int11'}}

        with pytest.raises(DeltaError) as excinfo:
            Delta(delta_dict, raise_errors=True) + t1

        expected_msg = NOT_VALID_NUMPY_TYPE.format("'int11'")
        assert expected_msg == str(excinfo.value)


class TestDeltaOther:

    def test_list_ignore_order_various_deltas1(self):
        t1 = [5, 1, 3, 1, 4, 4, 6]
        t2 = [7, 4, 4, 1, 3, 4, 8]

        delta_dict1 = {'iterable_items_added_at_indexes': {'root': {0: 7, 6: 8, 1: 4, 2: 4, 5: 4, 3: 1}}, 'iterable_items_removed_at_indexes': {'root': {0: 5, 6: 6}}}
        delta_dict2 = {'iterable_items_added_at_indexes': {'root': {1: 4, 2: 4, 5: 4, 3: 1}}, 'values_changed': {'root[6]': {'new_value': 7}, 'root[0]': {'new_value': 8}}}
        delta1 = Delta(delta_dict1)
        t1_plus_delta1 = t1 + delta1
        assert t1_plus_delta1 == t2
        delta2 = Delta(delta_dict2)
        t1_plus_delta2 = t1 + delta2
        assert t1_plus_delta2 == [8, 4, 4, 1, 3, 4, 7]

    def test_list_ignore_order_various_deltas2(self):
        t1 = (5, 1, 3, 1, 4, 4, 6)
        t2 = (7, 4, 4, 1, 3, 4, 8, 1)

        delta_dict1 = {'iterable_items_added_at_indexes': {'root': {0: 7, 6: 8, 1: 4, 2: 4, 5: 4}}, 'iterable_items_removed_at_indexes': {'root': {6: 6, 0: 5}}}
        delta_dict2 = {'iterable_items_added_at_indexes': {'root': {1: 4, 2: 4, 5: 4}}, 'values_changed': {'root[6]': {'new_value': 7}, 'root[0]': {'new_value': 8}}}
        delta1 = Delta(delta_dict1)
        t1_plus_delta1 = t1 + delta1
        assert t1_plus_delta1 == t2
        delta2 = Delta(delta_dict2)
        t1_plus_delta2 = t1 + delta2
        assert t1_plus_delta2 == (8, 4, 4, 1, 3, 4, 1, 7)

    def test_delta_view_and_to_delta_dict_are_equal_when_parameteres_passed(self):
        """
        This is a test that passes parameters in a dictionary instead of kwargs.
        Note that when parameters are passed as a dictionary, all of them even the ones that
        have default values need to be passed.
        """
        t1 = [4, 2, 2, 1]
        t2 = [4, 1, 1, 1]
        _parameters = {
            'ignore_order': True,
            'ignore_numeric_type_changes': False,
            'ignore_string_type_changes': False,
            'ignore_type_in_groups': [],
            'report_repetition': True,
            'exclude_paths': None,
            'exclude_regex_paths': None,
            'exclude_types': None,
            'exclude_types_tuple': None,
            'ignore_type_subclasses': False,
            'ignore_string_case': False,
            'exclude_obj_callback': None,
            'ignore_private_variables': True,
            'ignore_nan_inequality': False,
            'hasher': None,
            'significant_digits': None,
            'number_format_notation': 'f',
            'verbose_level': 1,
            'view': DELTA_VIEW,
            'max_passes': 10000000,
            'max_diffs': None,
            'number_to_string': number_to_string,
            'cache_tuning_sample_size': 500,
            'cache_size': 500,
            'cutoff_intersection_for_pairs': 0.6,
            'group_by': None,
        }

        expected = {'iterable_items_added_at_indexes': {'root': {1: 1, 2: 1, 3: 1}}, 'iterable_items_removed_at_indexes': {'root': {1: 2, 2: 2}}}
        diff1 = DeepDiff(t1, t2, _parameters=_parameters)
        assert expected == diff1

        _parameters['view'] = TEXT_VIEW
        diff2 = DeepDiff(t1, t2, _parameters=_parameters)
        assert expected == diff2._to_delta_dict()

    def test_verify_symmetry_and_get_elem_and_compare_to_old_value(self):
        """
        Test a specific case where path was a list of elements (in the form of tuples)
        and the item could not be found.
        """
        delta = Delta({}, verify_symmetry=True, raise_errors=True, log_errors=False)
        with pytest.raises(DeltaError) as excinfo:
            delta._get_elem_and_compare_to_old_value(
                obj={},
                path_for_err_reporting=(('root', GETATTR),),
                expected_old_value='Expected Value',
                action=GET,
                elem='key')
        assert VERIFICATION_MSG.format('root', 'Expected Value', 'not found', "'key'") == str(excinfo.value)

    def test_apply_delta_to_incompatible_object1(self):
        t1 = {1: {2: [4, 5]}}
        t2 = {1: {2: [4]}, 0: 'new'}

        diff = DeepDiff(t1, t2)
        delta = Delta(diff, raise_errors=True)

        t3 = []

        with pytest.raises(DeltaError) as excinfo:
            delta + t3
        assert "Unable to get the item at root[1][2][1]: list index out of range" == str(excinfo.value)
        assert [] == t3

    def test_apply_delta_to_incompatible_object3_errors_can_be_muted(self):
        t1 = {1: {2: [4]}}
        t2 = {1: {2: [4, 6]}}
        t3 = []

        diff = DeepDiff(t1, t2)

        delta2 = Delta(diff, raise_errors=False)
        t4 = delta2 + t3
        assert [] == t4

    def test_apply_delta_to_incompatible_object4_errors_can_be_muted(self):
        t1 = {1: {2: [4, 5]}}
        t2 = {1: {2: [4]}, 0: 'new'}
        t3 = []

        diff = DeepDiff(t1, t2)

        # The original delta was based on a diff between 2 dictionaries.
        # if we turn raise_errors=False, we can try to see what portions of the delta
        delta2 = Delta(diff, raise_errors=False)
        t4 = delta2 + t3
        assert ['new'] == t4

    def test_apply_delta_to_incompatible_object5_no_errors_detected(self):
        t1 = {3: {2: [4]}}
        t2 = {3: {2: [4]}, 0: 'new', 1: 'newer'}
        diff = DeepDiff(t1, t2)

        t3 = []
        # The original delta was based on a diff between 2 dictionaries.
        # if we turn raise_errors=True, and there are no errors, a delta can be applied fully to another object!
        delta2 = Delta(diff, raise_errors=True)
        t4 = delta2 + t3
        assert ['new', 'newer'] == t4

    def test_apply_delta_to_incompatible_object6_value_change(self):
        t1 = {1: {2: [4]}}
        t2 = {1: {2: [5]}}
        t3 = []

        diff = DeepDiff(t1, t2)

        delta2 = Delta(diff, raise_errors=False)
        t4 = delta2 + t3
        assert [] == t4

    def test_apply_delta_to_incompatible_object7_type_change(self):
        t1 = ['1']
        t2 = [1]
        t3 = ['a']

        diff = DeepDiff(t1, t2)

        delta2 = Delta(diff, raise_errors=False)
        t4 = delta2 + t3
        assert ['a'] == t4

    @mock.patch('deepdiff.delta.logger.error')
    def test_apply_delta_to_incompatible_object7_verify_symmetry(self, mock_logger):
        t1 = [1]
        t2 = [2]
        t3 = [3]

        diff = DeepDiff(t1, t2)

        delta2 = Delta(diff, raise_errors=False, verify_symmetry=True)
        t4 = delta2 + t3

        assert [2] == t4
        expected_msg = VERIFICATION_MSG.format('root[0]', 1, 3, VERIFY_SYMMETRY_MSG)
        mock_logger.assert_called_once_with(expected_msg)

    @mock.patch('deepdiff.delta.logger.error')
    def test_apply_delta_to_incompatible_object8_verify_symmetry_ignore_order(self, mock_logger):
        t1 = [1, 2, 'B', 3]
        t2 = [1, 2, 3, 5]
        t3 = []

        diff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True)

        delta2 = Delta(diff, raise_errors=False, verify_symmetry=True)
        t4 = delta2 + t3

        assert [5] == t4
        expected_msg = INDEXES_NOT_FOUND_WHEN_IGNORE_ORDER.format({3: 5})
        mock_logger.assert_called_once_with(expected_msg)

    @mock.patch('deepdiff.delta.logger.error')
    def test_apply_delta_to_incompatible_object9_ignore_order_and_verify_symmetry(self, mock_logger):
        t1 = [1, 2, 'B']
        t2 = [1, 2]
        t3 = [1, 2, 'C']

        diff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True)

        delta = Delta(diff, raise_errors=False, verify_symmetry=True)
        t4 = delta + t3

        assert [1, 2, 'C'] == t4
        expected_msg = FAIL_TO_REMOVE_ITEM_IGNORE_ORDER_MSG.format(2, 'root', 'B', 'C')
        mock_logger.assert_called_once_with(expected_msg)

    @mock.patch('deepdiff.delta.logger.error')
    def test_apply_delta_to_incompatible_object10_ignore_order(self, mock_logger):
        t1 = [1, 2, 'B']
        t2 = [1, 2]
        t3 = [1, 2, 'C']

        diff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True)

        # when verify_symmetry=False, we still won't remove the item that is different
        # than what we expect specifically when ignore_order=True when generating the diff.
        # The reason is that when ignore_order=True, we can' rely too much on the index
        # of the item alone to delete it. We need to make sure we are deleting the correct value.
        # The expected behavior is exactly the same as when verify_symmetry=True
        # specifically for when ignore_order=True AND an item is removed.
        delta = Delta(diff, raise_errors=False, verify_symmetry=False)
        t4 = delta + t3

        assert [1, 2, 'C'] == t4
        expected_msg = FAIL_TO_REMOVE_ITEM_IGNORE_ORDER_MSG.format(2, 'root', 'B', 'C')
        mock_logger.assert_called_once_with(expected_msg)

    @mock.patch('deepdiff.delta.logger.error')
    def test_apply_delta_to_incompatible_object11_ignore_order(self, mock_logger):
        t1 = [[1, 2, 'B']]
        t2 = [[1, 2]]
        t3 = {}

        diff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True)
        delta = Delta(diff, raise_errors=False, verify_symmetry=False)
        t4 = delta + t3

        assert {} == t4
        expected_msg = UNABLE_TO_GET_PATH_MSG.format('root[0][0]')
        mock_logger.assert_called_once_with(expected_msg)

    def test_delta_to_dict(self):
        t1 = [1, 2, 'B']
        t2 = [1, 2]
        diff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True)
        delta = Delta(diff, raise_errors=False, verify_symmetry=False)

        result = delta.to_dict()
        expected = {'iterable_items_removed_at_indexes': {'root': {2: 'B'}}}
        assert expected == result

    def test_class_type_change(self):
        t1 = CustomClass
        t2 = CustomClass2
        diff = DeepDiff(t1, t2, view=DELTA_VIEW)
        expected = {'type_changes': {'root': {'new_type': CustomClass2,
                    'old_type': CustomClass}}}

        assert expected == diff

    def test_numpy_type_invalid(self):
        t1 = np.array([[1, 2, 3], [4, 2, 2]], np.int8)
        diff = {
            'iterable_item_added': {'root[2]': [7, 8, 9]},
            'values_changed': {
                'root[0][2]': {
                    'new_value': 5
                },
                'root[1][1]': {
                    'new_value': 1
                }
            },
            '_numpy_paths': {
                'root': 'int88'
            }
        }

        delta = Delta(diff, raise_errors=True)
        with pytest.raises(DeltaError) as excinfo:
            delta + t1
        assert "'int88' is not a valid numpy type." == str(excinfo.value)

    def test_ignore_order_but_not_report_repetition(self):
        t1 = [1, 2, 'B', 3]
        t2 = [1, 2, 3, 5]

        with pytest.raises(ValueError) as excinfo:
            Delta(DeepDiff(t1, t2, ignore_order=True))

        assert DELTA_IGNORE_ORDER_NEEDS_REPETITION_REPORT == str(excinfo.value)

    def test_none_in_delta_object(self):
        t1 = {"a": None}
        t2 = {"a": 1}

        dump = Delta(DeepDiff(t1, t2)).dumps()
        delta = Delta(dump)
        assert t2 == delta + t1

    def test_delta_with_json_serializer(self):
        t1 = {"a": 1}
        t2 = {"a": 2}

        diff = DeepDiff(t1, t2)
        delta = Delta(diff, serializer=json.dumps)
        dump = delta.dumps()
        delta_reloaded = Delta(dump, deserializer=json.loads)
        assert t2 == delta_reloaded + t1

        the_file = io.StringIO()
        delta.dump(the_file)
        the_file.seek(0)

        delta_reloaded_again = Delta(delta_file=the_file, deserializer=json.loads)
        assert t2 == delta_reloaded_again + t1
