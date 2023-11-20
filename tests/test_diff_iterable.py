from deepdiff import DeepDiff
from deepdiff.helper import CannotCompare


class TestDiffIterableWithCompareFunc:

    @staticmethod
    def _compare_func(x, y, level=None):
        try:
            return x['uuid'] == y['uuid']
        except Exception:
            raise CannotCompare() from None

    def test_with_report_repetition_true(self, nested_c_t1, nested_c_t2, nested_c_result_report_repetition_true):
        ddiff = DeepDiff(
            nested_c_t1,
            nested_c_t2,
            ignore_order=True,
            iterable_compare_func=self._compare_func,
            report_repetition=True,
        )
        assert nested_c_result_report_repetition_true == ddiff

    def test_with_report_repetition_false(self, nested_c_t1, nested_c_t2, nested_c_result_report_repetition_false):
        ddiff = DeepDiff(
            nested_c_t1,
            nested_c_t2,
            ignore_order=True,
            iterable_compare_func=self._compare_func,
            report_repetition=False,
        )
        assert nested_c_result_report_repetition_false == ddiff
