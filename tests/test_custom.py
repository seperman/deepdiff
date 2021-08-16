import pytest
from deepdiff import DeepDiff


class customClass(object):

    def __init__(self, d: dict, l: list):
        self.dict = d
        self.dict['list'] = l

def custom_compare(c1: customClass, c2: customClass):
    return set(c1.dict['list']) == set(c2.dict['list'])


class TestCustomComparison():

    custom1 = customClass(d=dict(a=1, b=2), l=[1, 2, 3])
    custom2 = customClass(d=dict(c=3, d=4), l=[1, 2, 3, 2])

    def test_custom_equal(self):
        diff_res = DeepDiff(
            self.custom1, self.custom2,
            custom_comparison={customClass: custom_compare}
        )
        assert diff_res == {}

    def test_regular_compare(self):
        diff_res = DeepDiff(self.custom1, self.custom2)
        assert diff_res
