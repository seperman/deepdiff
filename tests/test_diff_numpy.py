import pytest
import numpy as np
from deepdiff import DeepDiff
from tests import parameterize_cases

NUMPY_CASES = {
    'case1': {
        't1': np.array([True, False, True, False], dtype=bool),
        't2': np.array([False, True, True, False], dtype=bool),
        'deepdiff_kwargs': {},
        'expected_result': {'values_changed': {'root[0]': {'new_value': False, 'old_value': True},
                            'root[1]': {'new_value': True, 'old_value': False}}},
    },
    'numpy_multi_dimensional1': {
        't1': np.array([[[1, 2, 3], [4, 5, 6]]], np.int32),
        't2': np.array([[[1, 2, 5], [3, 5, 6]]], np.int32),
        'deepdiff_kwargs': {},
        'expected_result': {'values_changed':
                            {'root[0][0][2]': {'new_value': 5, 'old_value': 3},
                             'root[0][1][0]': {'new_value': 3, 'old_value': 4}}},
    },

}


NUMPY_CASES_PARAMS = parameterize_cases(NUMPY_CASES)


class TestNumpy:

    @pytest.mark.parametrize('t1, t2, deepdiff_kwargs, expected_result', **NUMPY_CASES_PARAMS)
    def test_numpy(self, t1, t2, deepdiff_kwargs, expected_result):
        diff = DeepDiff(t1, t2, **deepdiff_kwargs)
        assert expected_result == diff
