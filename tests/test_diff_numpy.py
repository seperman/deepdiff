import pytest
import numpy as np
from deepdiff import DeepDiff
from tests import parameterize_cases

NUMPY_CASES = {
    'numpy_bools': {
        't1': np.array([True, False, True, False], dtype=bool),
        't2': np.array([False, True, True, False], dtype=bool),
        'deepdiff_kwargs': {},
        'expected_result': {'values_changed': {'root[0]': {'new_value': False, 'old_value': True},
                            'root[1]': {'new_value': True, 'old_value': False}}},
    },
    'numpy_bools_ignore_order': {
        't1': np.array([True, False, True, False], dtype=bool),
        't2': np.array([False, True, True, False], dtype=bool),
        'deepdiff_kwargs': {'ignore_order': True},
        'expected_result': {},
    },
    'numpy_multi_dimensional1': {
        't1': np.array([[[1, 2, 3], [4, 5, 6]]], np.int32),
        't2': np.array([[[1, 2, 5], [3, 5, 6]]], np.int32),
        'deepdiff_kwargs': {},
        'expected_result': {'values_changed':
                            {'root[0][0][2]': {'new_value': 5, 'old_value': 3},
                             'root[0][1][0]': {'new_value': 3, 'old_value': 4}}},
    },
    'numpy_array2_type_change': {
        't1': np.array([1, 2, 3], np.int8),
        't2': np.array([1, 2, 5], np.int32),
        'deepdiff_kwargs': {'verbose_level': 0},
        'expected_result': {'type_changes': {'root': {'old_type': np.int8, 'new_type': np.int32}}},
    },
    'numpy_array3_ignore_number_type_changes': {
        't1': np.array([1, 2, 3], np.int8),
        't2': np.array([1, 2, 5], np.int32),
        'deepdiff_kwargs': {'ignore_numeric_type_changes': True},
        'expected_result': {'values_changed': {'root[2]': {'new_value': 5, 'old_value': 3}}},
    },
    'numpy_array4_ignore_number_type_changes_and_ignore_order': {
        't1': np.array([1, 2, 3], np.int8),
        't2': np.array([3, 1, 2], np.int32),
        'deepdiff_kwargs': {'ignore_numeric_type_changes': True, 'ignore_order': True},
        'expected_result': {},
    },
    'numpy_array5_ignore_number_type_changes_and_ignore_order': {
        't1': np.array([1, 2, 4, 3], np.int8),
        't2': np.array([3, 1, 2, 5], np.int32),
        'deepdiff_kwargs': {'ignore_numeric_type_changes': True, 'ignore_order': True},
        'expected_result': {'iterable_item_added': {'root[3]': 5}, 'iterable_item_removed': {'root[2]': 4}},
    },
    'numpy_array6_ignore_order_and_report_repetition': {
        't1': np.array([1, 2, 3, 3], np.int8),
        't2': np.array([3, 1, 2, 5], np.int8),
        'deepdiff_kwargs': {'report_repetition': True, 'ignore_order': True},
        'expected_result': {'iterable_item_added': {'root[3]': 5},
                            'repetition_change': {'root[2]': {'old_repeat': 2, 'new_repeat': 1,
                                                              'old_indexes': [2, 3], 'new_indexes': [0], 'value': 3}}},
    },
}


NUMPY_CASES_PARAMS = parameterize_cases('t1, t2, deepdiff_kwargs, expected_result', NUMPY_CASES)


class TestNumpy:

    @pytest.mark.parametrize(**NUMPY_CASES_PARAMS)
    def test_numpy(self, t1, t2, deepdiff_kwargs, expected_result):
        diff = DeepDiff(t1, t2, **deepdiff_kwargs)
        assert expected_result == diff
