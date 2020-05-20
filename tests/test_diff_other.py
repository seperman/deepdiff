import pytest
import datetime
from time import sleep
from unittest import mock
from deepdiff.model import DiffLevel
from deepdiff.diff import DeepDiff, PROGRESS_MSG, INVALID_VIEW_MSG


class SlowDiffLevel(DiffLevel):
    is_run = False

    def __init__(self, *args, **kwargs):
        sleep(.1)
        super().__init__(*args, **kwargs)


class TestDiffOther:

    @mock.patch('deepdiff.diff.DiffLevel', side_effect=SlowDiffLevel)
    def test_repeated_timer(self, MockDiffLevel):
        t1 = [1, [2]]
        t2 = [1, [3]]

        progress_logger = mock.Mock()
        DeepDiff(t1, t2, log_frequency_in_sec=0.02, progress_logger=progress_logger)
        assert PROGRESS_MSG.format(0, 0, 0) == progress_logger.call_args[0][0]

    def test_invalid_view(self):
        t1 = [1]
        t2 = [2]
        with pytest.raises(ValueError) as excinfo:
            DeepDiff(t1, t2, view='blah')
        assert str(excinfo.value) == INVALID_VIEW_MSG.format('blah')

    def test_truncate_datetime(self):
        d1 = {'a' : datetime.datetime(2020, 5, 17, 22, 15, 34, 913070)}
        d2 = {'a' : datetime.datetime(2020, 5, 17, 22, 15, 39, 296583)}
        res = DeepDiff(d1, d2, truncate_datetime='minute')
        assert res == {}

        res = DeepDiff(d1, d2, truncate_datetime='second')
        assert res['values_changed']["root['a']"]['new_value'] == 1589753739.0

        d1 = {'a' : datetime.time(22, 15, 34, 913070)}
        d2 = {'a' : datetime.time(22, 15, 39, 296583)}

        res = DeepDiff(d1, d2, truncate_datetime='minute')
        assert res == {}

        res = DeepDiff(d1, d2, truncate_datetime='second')
        assert res['values_changed']["root['a']"]['new_value'] == 80139
