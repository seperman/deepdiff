import pytest
import datetime
from decimal import Decimal
from deepdiff import DeepDiff
from deepdiff.helper import np
from deepdiff.diff import DELTA_VIEW, CUTOFF_RANGE_ERROR_MSG
from deepdiff.deephash import sha256hex
from deepdiff.distance import (
    _get_item_length, _get_numbers_distance, get_numeric_types_distance,
    _get_numpy_array_distance, DISTANCE_CALCS_NEEDS_CACHE)
from tests import CustomClass


class TestDeepDistance:

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
            5
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
    def test_item_length(self, diff, expected_length):
        length = _get_item_length(diff)
        assert expected_length == length

    def test_distance_of_the_same_objects(self):
        t1 = [{1, 2, 3}, {4, 5, 6}]
        t2 = [{4, 5, 6}, {1, 2, 3}]
        ddiff = DeepDiff(t1, t2, ignore_order=True, cache_purge_level=0)
        assert {} == ddiff
        assert 0 == _get_item_length(ddiff)
        assert '0' == str(ddiff._get_rough_distance())[:10]
        assert 9 == ddiff._DistanceMixin__get_item_rough_length(ddiff.t1)
        assert 9 == ddiff._DistanceMixin__get_item_rough_length(ddiff.t2)

    def test_distance_of_list_sets(self):
        t1 = [{1, 2, 3}, {4, 5}]
        t2 = [{4, 5, 6}, {1, 2, 3}]
        ddiff = DeepDiff(t1, t2, ignore_order=True, cache_purge_level=0)
        delta = ddiff._to_delta_dict(report_repetition_required=False)
        assert {'set_item_added': {'root[1]': {6}}} == delta
        assert 1 == _get_item_length(ddiff)
        assert '0.05882352' == str(ddiff._get_rough_distance())[:10]
        assert 8 == ddiff._DistanceMixin__get_item_rough_length(ddiff.t1)
        assert 9 == ddiff._DistanceMixin__get_item_rough_length(ddiff.t2)

    @pytest.mark.parametrize('verbose_level', [0, 1, 1])
    def test_distance_of_list_sets2(self, verbose_level):
        t1 = [{1, 2, 3}, {4, 5}, {1}]
        t2 = [{4, 5, 6}, {1, 2, 3}, {1, 4}]
        ddiff = DeepDiff(t1, t2, ignore_order=True, verbose_level=verbose_level,
                         get_deep_distance=True, cache_purge_level=0)
        delta = ddiff._to_delta_dict(report_repetition_required=False)
        assert {'set_item_added': {'root[2]': {4}, 'root[1]': {6}}} == delta
        assert 2 == _get_item_length(ddiff)
        assert '0.09090909' == str(ddiff['deep_distance'])[:10]
        assert 10 == ddiff._DistanceMixin__get_item_rough_length(ddiff.t1)
        assert 12 == ddiff._DistanceMixin__get_item_rough_length(ddiff.t2)

    @pytest.mark.parametrize('verbose_level', [0, 1, 1])
    def test_distance_of_list_sets_and_strings(self, verbose_level):
        t1 = [{1, 2, 3}, {4, 5, 'hello', 'right!'}, {4, 5, (2, 4, 7)}]
        t2 = [{4, 5, 6, (2, )}, {1, 2, 3}, {5, 'hello', 'right!'}]
        ddiff = DeepDiff(t1, t2, ignore_order=True, view=DELTA_VIEW, verbose_level=verbose_level)
        delta = ddiff._to_delta_dict(report_repetition_required=False)
        expected = {
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
        }
        assert expected == ddiff
        # If the diff was in delta view, spitting out another delta dict should produce identical results.
        assert delta == ddiff
        assert 10 == _get_item_length(ddiff)

    def test_distance_of_tuple_in_list(self):
        t1 = {(2,), 4, 5, 6}
        t2 = {'right!', 'hello', 4, 5}
        diff = DeepDiff(t1, t2, ignore_order=True, view=DELTA_VIEW, get_deep_distance=True)
        assert {'set_item_removed': {'root': {(2,), 6}}, 'set_item_added': {'root': {'hello', 'right!'}}} == diff
        # delta view should not have the distance info in it
        assert 'get_deep_distance' not in diff

    def test_get_item_length_when_loops1(self):
        t1 = [[1, 2, 1, 3]]
        t1.append(t1)

        item_length = _get_item_length(t1)
        assert 8 == item_length

    def test_get_item_length_when_loops2(self):
        t1 = {1: 1}
        t1[2] = t1

        item_length = _get_item_length(t1)
        assert 2 == item_length

    def test_get_distance_works_event_when_ignore_order_is_false1(self):
        t1 = 10
        t2 = 110
        diff = DeepDiff(t1, t2, get_deep_distance=True)
        dist = diff['deep_distance']
        assert dist == Decimal('0.25')

    def test_get_distance_works_event_when_ignore_order_is_false2(self):
        t1 = ["a", "b"]
        t2 = ["a", "b", "c"]
        diff = DeepDiff(t1, t2, get_deep_distance=True)
        dist = diff['deep_distance']
        assert str(dist)[:4] == '0.14'
        assert set(diff.keys()) == {'iterable_item_added', 'deep_distance'}

    def test_get_distance_works_event_when_ignore_order_is_false3(self):
        t1 = ["a", "b"]
        t2 = ["a", "b", "c", "d"]
        diff = DeepDiff(t1, t2, get_deep_distance=True)
        dist = diff['deep_distance']
        assert str(dist)[:4] == '0.25'

    def test_get_distance_works_event_when_ignore_order_and_different_hasher(self):
        t1 = ["a", "b", 2]
        t2 = ["a", "b", "c", 2.2]
        diff = DeepDiff(t1, t2, ignore_order=True, get_deep_distance=True,
                        cache_size=100, hasher=sha256hex)
        dist = diff['deep_distance']
        assert str(dist)[:4] == '0.44'

    def test_get_distance_does_not_care_about_the_size_of_string(self):
        t1 = ["a", "b"]
        t2 = ["a", "b", "c", "dddddd"]
        diff = DeepDiff(t1, t2, get_deep_distance=True)
        dist = diff['deep_distance']
        assert str(dist)[:4] == '0.25'

    def test_get_item_length_custom_class1(self):
        item = CustomClass(a=10)
        item_length = _get_item_length(item)
        assert 2 == item_length

    def test_get_item_length_custom_class2_loop(self):
        item = CustomClass(a=10)
        item.b = item
        item_length = _get_item_length(item)
        assert 2 == item_length

    @pytest.mark.parametrize('num1, num2, max_, expected', [
        (10.0, 10, 1, 0),
        (Decimal('10.1'), Decimal('10.2'), 1, 0.004926108374384236453201970443),
        (Decimal(10), Decimal(-10), 1, 1),
        (2, 3, 1, 0.2),
        (10, -10, .1, .1),
        (10, -10.1, .1, .1),
        (10, -10.1, .3, 0.3),
    ])
    def test_get_numbers_distance(self, num1, num2, max_, expected):
        result = _get_numbers_distance(num1, num2, max_)
        assert abs(expected - result) < 0.0001

    @pytest.mark.parametrize('arr1, arr2', [
        (np.array([4.1978, 4.1979, 4.1980]), np.array([4.1971, 4.1879, 4.1981])),
        (np.array([1, 2, 4]), np.array([4, 2, 3])),
    ])
    def test_numpy_distance_vs_get_numbers_distance(self, arr1, arr2):
        dist_arr = _get_numpy_array_distance(arr1, arr2)
        for i in range(3):
            assert dist_arr[i] == _get_numbers_distance(arr1[i], arr2[i])

    @pytest.mark.parametrize('num1, num2, max_, expected', [
        (10, -10.1, .3, 0.3),
        (datetime.datetime(2022, 4, 10, 0, 40, 41, 357857), datetime.datetime(2022, 4, 10, 0, 40, 41, 357857) + datetime.timedelta(days=100), 1, 0.002707370659621624),
        (1589703146.9556487, 1001589703146.9557, 1, 0.9968306702929068),
        (datetime.time(10, 11), datetime.time(12, 11), .5, 0.0447093889716),
        (datetime.timedelta(days=2), datetime.timedelta(12, 11), .5, 0.35714415626180646),
        (datetime.date(2018, 1, 1), datetime.date(2020, 1, 10), 1, 0.0005013129787148886),
    ])
    def test_get_numeric_types_distance(self, num1, num2, max_, expected):
        result = get_numeric_types_distance(num1, num2, max_)
        assert abs(expected - result) < 0.0001

    def test_get_rough_length_after_cache_purge(self):
        diff = DeepDiff([1], ['a'])
        with pytest.raises(RuntimeError) as excinfo:
            diff._get_rough_distance()
        assert DISTANCE_CALCS_NEEDS_CACHE == str(excinfo.value)

    def test_cutoff_distance_for_pairs_range(self):
        with pytest.raises(ValueError) as excinfo:
            DeepDiff(1, 2, cutoff_distance_for_pairs=2)
        assert CUTOFF_RANGE_ERROR_MSG == str(excinfo.value)
