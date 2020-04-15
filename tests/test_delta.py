import pytest
from unittest import mock
from deepdiff import Delta
from deepdiff.delta import (
    GETATTR, GET, INDEX_NOT_FOUND_TO_ADD_MSG, VERIFICATION_MSG, not_found, _path_to_elements)


@pytest.mark.parametrize('path, expected', [
    ("root[4]['b'][3]", [(4, GET), ('b', GET), (3, GET)]),
    ("root[4].b[3]", [(4, GET), ('b', GETATTR), (3, GET)]),
    ("root[4].b['a3']", [(4, GET), ('b', GETATTR), ('a3', GET)]),
    ("root[4.3].b['a3']", [(4.3, GET), ('b', GETATTR), ('a3', GET)]),
    ("root.a.b", [('a', GETATTR), ('b', GETATTR)]),
    ("root.hello", [('hello', GETATTR)]),
    ("root['a\]b']", [('a\]b', GET)]),
])
def test_path_to_elements(path, expected):
    result = _path_to_elements(path)
    assert expected == result


class TestDelta:

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

        delta2 = Delta(diff, verify_old_value=True, raise_errors=True, log_errors=False)
        with pytest.raises(ValueError) as excinfo:
            delta2 + t1
        assert expected_msg == str(excinfo.value)
        assert not mock_logger.called

        delta3 = Delta(diff, verify_old_value=True, raise_errors=True, log_errors=True)
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

        expected_msg = VERIFICATION_MSG.format('root[2]', 5, 6)

        delta = Delta(diff, verify_old_value=True, raise_errors=True)
        with pytest.raises(ValueError) as excinfo:
            delta + t1
        assert expected_msg == str(excinfo.value)

        delta2 = Delta(diff, verify_old_value=False)
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
        expected_msg = VERIFICATION_MSG.format("root[3]", 'to_be_removed2', not_found)

        delta = Delta(diff, verify_old_value=True, raise_errors=True)
        with pytest.raises(ValueError) as excinfo:
            delta + t1
        assert expected_msg == str(excinfo.value)

        delta2 = Delta(diff, verify_old_value=False, raise_errors=True)
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
        expected_msg = VERIFICATION_MSG.format("root[4]['b'][2]", 'to_be_removed', 'wrong')

        delta = Delta(diff, verify_old_value=True, raise_errors=True)
        with pytest.raises(ValueError) as excinfo:
            delta + t1
        assert expected_msg == str(excinfo.value)

        delta2 = Delta(diff, verify_old_value=False, raise_errors=True)
        assert t1 + delta2 == t2
