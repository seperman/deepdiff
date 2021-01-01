import pytest
import datetime
from time import sleep
from unittest import mock
from deepdiff.model import DiffLevel
from deepdiff.diff import (
    DeepDiff, PROGRESS_MSG, INVALID_VIEW_MSG, VERBOSE_LEVEL_RANGE_MSG,
    PURGE_LEVEL_RANGE_MSG)


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
        d1 = {'a': datetime.datetime(2020, 5, 17, 22, 15, 34, 913070)}
        d2 = {'a': datetime.datetime(2020, 5, 17, 22, 15, 39, 296583)}
        res = DeepDiff(d1, d2, truncate_datetime='minute')
        assert res == {}

        res = DeepDiff(d1, d2, truncate_datetime='second')
        expected = datetime.datetime(2020, 5, 17, 22, 15, 39, tzinfo=datetime.timezone.utc)
        assert res['values_changed']["root['a']"]['new_value'] == expected

        d1 = {'a': datetime.time(22, 15, 34, 913070)}
        d2 = {'a': datetime.time(22, 15, 39, 296583)}

        res = DeepDiff(d1, d2, truncate_datetime='minute')
        assert res == {}

        res = DeepDiff(d1, d2, truncate_datetime='second')
        assert res['values_changed']["root['a']"]['new_value'] == 80139

    def test_invalid_verbose_level(self):
        with pytest.raises(ValueError) as excinfo:
            DeepDiff(1, 2, verbose_level=5)
        assert str(excinfo.value) == VERBOSE_LEVEL_RANGE_MSG

    def test_invalid_cache_purge_level(self):
        with pytest.raises(ValueError) as excinfo:
            DeepDiff(1, 2, cache_purge_level=5)
        assert str(excinfo.value) == PURGE_LEVEL_RANGE_MSG

    def test_cache_purge_level_max(self):
        diff = DeepDiff([1], [2], cache_purge_level=1)
        assert len(diff.__dict__.keys()) > 10
        diff2 = DeepDiff([1], [2], cache_purge_level=2)
        assert not diff2.__dict__
        expected = {'values_changed': {'root[0]': {'new_value': 2, 'old_value': 1}}}
        assert expected == diff2

        diff2 = DeepDiff([1], [2], cache_purge_level=2, view='tree')
        assert not diff2.__dict__
        assert list(diff2.keys()) == ['values_changed']

    def test_path_cache(self):
        diff = DeepDiff([1], [2], cache_purge_level=2, view='tree')
        path1 = diff['values_changed'][0].path()
        path2 = diff['values_changed'][0].path()
        assert 'root[0]' == path1 == path2

    def test_bool_str(self):
        t1 = {'key1': True}
        t2 = {'key1': 'Yes'}
        diff = DeepDiff(t1, t2, ignore_type_in_groups=[(bool, str)],
                        ignore_numeric_type_changes=True)
        expected = {'values_changed':
                        {"root['key1']":
                             {'new_value': 'Yes', 'old_value': True}
                        }
                    }
        assert diff == expected

    def test_get_distance_cache_key(self):
        result = DeepDiff._get_distance_cache_key(added_hash=5, removed_hash=20)
        assert b'0x14--0x5dc' == result
