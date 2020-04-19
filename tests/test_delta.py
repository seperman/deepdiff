import pytest
from decimal import Decimal
from unittest import mock
from deepdiff import Delta, DeepDiff
from deepdiff.delta import (
    DISABLE_DELTA, DELTA_SKIP_MSG, INDEX_NOT_FOUND_TO_ADD_MSG,
    VERIFICATION_MSG, VERIFY_SYMMETRY_MSG, not_found)


def parameterize_cases(cases):
    return [tuple(i.values()) for i in cases]


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

        expected_msg = INDEX_NOT_FOUND_TO_ADD_MSG.format(20, 'root[20]')

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

    def test_list_difference_delta(self):
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

    # def test_frozenset_delta(self):
    #     t1 = frozenset([1, 2, 'B'])
    #     t2 = frozenset([1, 2, 3, 5])
    #     ddiff = DeepDiff(t1, t2)
    #     import pytest; pytest.set_trace()
    #     aa = ddiff.to_dict()
    #     diff = {
    #         'set_item_added': {'root[3]', 'root[5]'},
    #         'set_item_removed': {"root['B']"}
    #     }
    #     delta = Delta(diff, verify_symmetry=True, raise_errors=True)
    #     assert t1 + delta == t2


DELTA_CASES = [
    {
        't1': frozenset([1, 2, 'B']),
        't2': frozenset([1, 2, 3, 5]),
        'deepdiff_kwargs': {},
        'to_delta_kwargs': {},
        'expected_delta_dict': {'set_item_removed': {'root': {'B'}}, 'set_item_added': {'root': {3, 5}}},
    },
    {
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
    {
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
    {
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
    {
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
    {
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
]


DELTA_CASES_PARAMS = parameterize_cases(DELTA_CASES)


@pytest.mark.skipif(DISABLE_DELTA, reason=DELTA_SKIP_MSG)
class TestDelta:

    @pytest.mark.parametrize('t1, t2, deepdiff_kwargs, to_delta_kwargs, expected_delta_dict', DELTA_CASES_PARAMS)
    def test_delta_cases(self, t1, t2, deepdiff_kwargs, to_delta_kwargs, expected_delta_dict):
        diff = DeepDiff(t1, t2, **deepdiff_kwargs)
        delta_dict = diff.to_delta_dict(**to_delta_kwargs)
        assert expected_delta_dict == delta_dict
        delta = Delta(diff, verify_symmetry=False, raise_errors=True)
        assert t1 + delta == t2
