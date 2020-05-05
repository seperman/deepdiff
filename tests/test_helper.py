#!/usr/bin/env python
import pytest
import numpy as np
from decimal import Decimal
from deepdiff.helper import (
    short_repr, number_to_string, get_numpy_ndarray_rows, cartesian_product_of_shape, literal_eval_extended)


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
