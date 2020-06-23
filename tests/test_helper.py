#!/usr/bin/env python
import pytest
import datetime
import numpy as np
from decimal import Decimal
from deepdiff.helper import (
    short_repr, number_to_string, get_numpy_ndarray_rows,
    cartesian_product_of_shape, literal_eval_extended,
    not_found, OrderedSetPlus, diff_numpy_array, cartesian_product_numpy,
    get_truncate_datetime, datetime_normalize
)


class TestHelper:
    """Helper Tests."""

    def test_short_repr_when_short(self):

        item = {1: 2}
        output = short_repr(item)
        assert output == '{1: 2}'

    def test_short_repr_when_long(self):

        item = {'Eat more': 'burritos'}
        output = short_repr(item)
        assert output == "{'Eat more':...}"

    @pytest.mark.parametrize("t1, t2, significant_digits, expected_result",
                             [
                                 (10, 10.0, 5, True),
                                 (10, 10.2, 5, ('10.00000', '10.20000')),
                                 (10, 10.2, 0, True),
                                 (Decimal(10), 10, 0, True),
                                 (Decimal(10), 10, 10, True),
                                 (Decimal(10), 10.0, 0, True),
                                 (Decimal(10), 10.0, 10, True),
                                 (Decimal('10.0'), 10.0, 5, True),
                                 (Decimal('10.01'), 10.01, 1, True),
                                 (Decimal('10.01'), 10.01, 2, True),
                                 (Decimal('10.01'), 10.01, 5, True),
                                 (Decimal('10.01'), 10.01, 8, True),
                                 (Decimal('10.010'), 10.01, 3, True),
                                 (Decimal('100000.1'), 100000.1, 0, True),
                                 (Decimal('100000.1'), 100000.1, 1, True),
                                 (Decimal('100000.1'), 100000.1, 5, True),
                                 (Decimal('100000'), 100000.1, 0, True),
                                 (Decimal('100000'), 100000.1, 1, ('100000.0', '100000.1')),
                             ])
    def test_number_to_string_decimal_digits(self, t1, t2, significant_digits, expected_result):
        st1 = number_to_string(t1, significant_digits=significant_digits, number_format_notation="f")
        st2 = number_to_string(t2, significant_digits=significant_digits, number_format_notation="f")
        if expected_result is True:
            assert st1 == st2
        else:
            assert st1 == expected_result[0]
            assert st2 == expected_result[1]

    def test_number_to_string_with_invalid_notation(self):
        with pytest.raises(ValueError):
            number_to_string(10, significant_digits=4, number_format_notation='blah')

    def test_cartesian_product_of_shape(self):
        result = list(cartesian_product_of_shape([2, 1, 3]))
        assert [(0, 0, 0), (0, 0, 1), (0, 0, 2), (1, 0, 0), (1, 0, 1), (1, 0, 2)] == result

    def test_get_numpy_ndarray_rows(self):
        obj = np.array([[[1, 2, 3], [4, 5, 6]]], np.int32)
        path0 = (0, 0)
        row0 = np.array([1, 2, 3], dtype=np.int32)
        (path0, row0) = next(get_numpy_ndarray_rows(obj))

        path1 = (0, 1)
        row1 = np.array([4, 5, 6], dtype=np.int32)
        (path1, row1) = next(get_numpy_ndarray_rows(obj))

    @pytest.mark.parametrize('item, expected', [
        ('10', 10),
        ("Decimal('10.1')", Decimal('10.1')),
    ])
    def test_literal_eval_extended(self, item, expected):
        result = literal_eval_extended(item)
        assert expected == result

    def test_not_found_inequality(self):
        assert not_found != not_found

    def test_ordered_set_plus_lpop(self):
        obj = OrderedSetPlus([1, 1, 2])
        assert 1 == obj.lpop()
        assert 2 == obj.lpop()
        with pytest.raises(KeyError) as excinfo:
            obj.lpop()
        assert str(excinfo.value) == "'lpop from an empty set'"

    @pytest.mark.parametrize('array1, array2, expected', [
        (np.array([3, 1, 2, 4, 3]), np.array([5, 2, 4]), [3, 1, 3]),
        (np.array([5, 2, 4]), np.array([3, 1, 2, 4, 3]), [5]),
    ])
    def test_diff_numpy_array(self, array1, array2, expected):
        result = diff_numpy_array(array1, array2)
        assert expected == result.tolist()

    def test_cartesian_product_numpy(self):
        result = cartesian_product_numpy(np.array([3, 1, 2, 4, 3]), np.array([5, 2, 4]))
        expected = [
            [3, 5],
            [3, 2],
            [3, 4],
            [1, 5],
            [1, 2],
            [1, 4],
            [2, 5],
            [2, 2],
            [2, 4],
            [4, 5],
            [4, 2],
            [4, 4],
            [3, 5],
            [3, 2],
            [3, 4]]
        assert expected == result.tolist()

    def test_get_truncate_datetime(self):
        result = get_truncate_datetime('hour')
        assert 'hour' == result
        with pytest.raises(ValueError):
            get_truncate_datetime('blah')

    @pytest.mark.parametrize('truncate_datetime, obj, expected', [
        ('hour',
         datetime.datetime(2020, 5, 30, 7, 28, 51, 698308),
         datetime.datetime(2020, 5, 30, 7, 0, tzinfo=datetime.timezone.utc)),
        ('day',
         datetime.datetime(2020, 5, 30, 7, 28, 51, 698308),
         datetime.datetime(2020, 5, 30, 0, 0, tzinfo=datetime.timezone.utc)),
    ])
    def test_datetime_normalize(self, truncate_datetime, obj, expected):
        result = datetime_normalize(truncate_datetime, obj)
        assert expected == result
