import pytest
from decimal import Decimal
from deepdiff.diff import DeepDiff, DELTA_VIEW, _get_diff_length


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
        length = _get_diff_length(diff)
        assert expected_length == length


class TestDeltaView:

    def test_delta_view_of_the_same_objects(self):
        t1 = [{1, 2, 3}, {4, 5, 6}]
        t2 = [{4, 5, 6}, {1, 2, 3}]
        ddiff = DeepDiff(t1, t2, ignore_order=True, view=DELTA_VIEW)
        assert {} == ddiff
        assert 0 == _get_diff_length(ddiff)
        assert '0' == str(ddiff.get_rough_distance())[:10]
        assert 9 == ddiff._DeepDiff__get_item_rough_length(ddiff.t1)
        assert 9 == ddiff._DeepDiff__get_item_rough_length(ddiff.t2)

    def test_delta_view_of_list_sets(self):
        t1 = [{1, 2, 3}, {4, 5}]
        t2 = [{4, 5, 6}, {1, 2, 3}]
        ddiff = DeepDiff(t1, t2, ignore_order=True, view=DELTA_VIEW)
        assert {'set_item_added': {'root[1]': {6}}} == ddiff
        assert 1 == _get_diff_length(ddiff)
        assert '0.05882352' == str(ddiff.get_rough_distance())[:10]
        assert 8 == ddiff._DeepDiff__get_item_rough_length(ddiff.t1)
        assert 9 == ddiff._DeepDiff__get_item_rough_length(ddiff.t2)

    def test_delta_view_of_list_sets2(self):
        t1 = [{1, 2, 3}, {4, 5}, {1}]
        t2 = [{4, 5, 6}, {1, 2, 3}, {1, 4}]
        ddiff = DeepDiff(t1, t2, ignore_order=True, view=DELTA_VIEW)
        assert {'set_item_added': {'root[2]': {4}, 'root[1]': {6}}} == ddiff
        assert 2 == _get_diff_length(ddiff)
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
        assert 6 == _get_diff_length(ddiff)
