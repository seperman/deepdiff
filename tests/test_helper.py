#!/usr/bin/env python
import pytest
from decimal import Decimal
from deepdiff.helper import short_repr, number_to_string


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
