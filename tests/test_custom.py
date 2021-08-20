import pytest
from deepdiff import DeepDiff


class CustomClass(object):

    def __init__(self, d: dict, l: list):
        self.dict = d
        self.dict['list'] = l

    def __repr__(self):
        return "Class list is " + str(self.dict['list'])


def custom_compare(c1: CustomClass, c2: CustomClass):
    return set(c1.dict['list']) == set(c2.dict['list'])


class TestCustomComparison():

    custom1 = CustomClass(d=dict(a=1, b=2), l=[1, 2, 3])
    custom2 = CustomClass(d=dict(c=3, d=4), l=[1, 2, 3, 2])
    custom3 = CustomClass(d=dict(a=1, b=2), l=[1, 2, 3, 4])

    def test_custom_equal(self):
        diff_res = DeepDiff(
            self.custom1, self.custom2,
            custom_comparison={CustomClass: custom_compare}
        )
        assert diff_res == {}

    def test_custom_non_equal(self):
        diff_res = DeepDiff(
            self.custom1, self.custom3,
            custom_comparison={CustomClass: custom_compare}
        )
        assert diff_res

    def test_regular_compare(self):
        diff_res = DeepDiff(self.custom1, self.custom2)
        assert diff_res
