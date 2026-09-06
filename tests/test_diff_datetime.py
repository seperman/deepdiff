import pytz
import pytest
import numpy as np
from datetime import date, datetime, time, timedelta, timezone
from deepdiff import DeepDiff


class TestDiffDatetime:
    def test_datetime_diff(self):
        """Testing for the correct setting and usage of epsilon."""
        d1 = {"a": datetime(2023, 7, 5, 10, 11, 12)}
        d2 = {"a": datetime(2023, 7, 5, 10, 11, 12)}
        res = DeepDiff(d1, d2)
        assert res == {}

        res = DeepDiff(d1, d2, ignore_numeric_type_changes=True)
        assert res == {}

        d1 = {"a": datetime(2023, 7, 5, 10, 11, 12)}
        d2 = {"a": datetime(2023, 7, 5, 11, 11, 12)}
        res = DeepDiff(d1, d2)
        expected = {
            "values_changed": {
                "root['a']": {
                    "new_value": datetime(2023, 7, 5, 11, 11, 12, tzinfo=timezone.utc),
                    "old_value": datetime(2023, 7, 5, 10, 11, 12, tzinfo=timezone.utc),
                }
            }
        }
        assert res == expected


    def test_date_diff(self):
        """Testing for the correct setting and usage of epsilon."""
        d1 = {"a": date(2023, 7, 5)}
        d2 = {"a": date(2023, 7, 5)}
        res = DeepDiff(d1, d2)
        assert res == {}

        # this usage failed in version >=6.0, <=6.3.0
        res = DeepDiff(d1, d2, ignore_numeric_type_changes=True)
        assert res == {}

        d1 = {"a": date(2023, 7, 5)}
        d2 = {"a": date(2023, 7, 6)}
        res = DeepDiff(d1, d2)
        expected = {
            "values_changed": {
                "root['a']": {
                    "new_value": date(2023, 7, 6),
                    "old_value": date(2023, 7, 5),
                }
            }
        }
        assert res == expected

    def test_time_diff(self):
        """Testing for the correct setting and usage of epsilon."""
        d1 = {"a": time(10, 11, 12)}
        d2 = {"a": time(10, 11, 12)}
        res = DeepDiff(d1, d2)
        assert res == {}

        res = DeepDiff(d1, d2, ignore_numeric_type_changes=True)
        assert res == {}

        d1 = {"a": time(10, 11, 12)}
        d2 = {"a": time(11, 11, 12)}
        res = DeepDiff(d1, d2)
        expected = {
            "values_changed": {
                "root['a']": {
                    "new_value": time(11, 11, 12),
                    "old_value": time(10, 11, 12),
                }
            }
        }
        assert res == expected

    def test_diffs_datetimes_different_timezones(self):
        dt_utc = datetime(2025, 2, 3, 12, 0, 0, tzinfo=pytz.utc)  # UTC timezone
        # Convert it to another timezone (e.g., New York)
        dt_ny = dt_utc.astimezone(pytz.timezone('America/New_York'))
        assert dt_utc == dt_ny
        diff = DeepDiff(dt_utc, dt_ny)
        assert not diff

        t1 = [dt_utc, dt_ny]
        t2 = [dt_ny, dt_utc]
        assert not DeepDiff(t1, t2)
        assert not DeepDiff(t1, t2, ignore_order=True)

        t2 = [dt_ny, dt_utc, dt_ny]
        assert not DeepDiff(t1, t2, ignore_order=True)

    def test_diffs_datetimes_in_different_timezones(self):
        dt_utc = datetime(2025, 2, 3, 12, 0, 0, tzinfo=pytz.utc)  # UTC timezone
        dt_utc2 = datetime(2025, 2, 3, 11, 0, 0, tzinfo=pytz.utc)  # UTC timezone
        dt_ny = dt_utc.astimezone(pytz.timezone('America/New_York'))
        dt_ny2 = dt_utc2.astimezone(pytz.timezone('America/New_York'))
        diff = DeepDiff(dt_ny, dt_ny2)
        assert {
            "values_changed": {
                "root": {
                    "new_value": dt_utc2,
                    "old_value": dt_utc,
                }
            }
        } == diff
        diff2 = DeepDiff(dt_ny, dt_ny2, default_timezone=pytz.timezone('America/New_York'))
        assert {
            "values_changed": {
                "root": {
                    "new_value": dt_ny2,
                    "old_value": dt_ny,
                }
            }
        } == diff2

    def test_datetime_within_array_with_timezone_diff(self):
        d1 = [datetime(2020, 8, 31, 13, 14, 1)]
        d2 = [datetime(2020, 8, 31, 13, 14, 1, tzinfo=timezone.utc)]

        assert d1 != d2, "Python doesn't think these are the same datetimes"
        assert not DeepDiff(d1, d2)
        assert not DeepDiff(d1, d2, ignore_order=True)
        assert not DeepDiff(d1, d2, truncate_datetime='second')


@pytest.mark.parametrize("key, other_key", [
    (datetime(2020, 5, 17, 22, 15), datetime(2020, 5, 17, 22, 15, 0, 1)),
    (datetime(2020, 5, 17, tzinfo=timezone.utc), datetime(2020, 5, 17, microsecond=1, tzinfo=timezone.utc)),
    (date(2020, 5, 17), date(2020, 5, 18)),
    (time(22, 15), time(22, 15, microsecond=1)),
    (timedelta(seconds=1), timedelta(seconds=1, microseconds=1)),
    (np.datetime64('2020-05-17T22:15:00.000000'), np.datetime64('2020-05-17T22:15:00.000001')),
])
@pytest.mark.parametrize("flag", [
    "ignore_numeric_type_changes", "ignore_string_case", "ignore_string_type_changes",
])
@pytest.mark.parametrize("ignore_order", [False, True])
def test_temporal_dict_keys_preserve_identity_with_numeric_precision(key, other_key, flag, ignore_order):
    """Key cleaning must not round temporal keys or merge distinct instants."""
    t1 = {key: 1, other_key: 2}
    t2 = {key: 1, other_key: 3}
    if ignore_order:
        t1, t2 = [t1], [t2]
    result = DeepDiff(t1, t2, significant_digits=0, view='tree', ignore_order=ignore_order, **{flag: True})
    assert set(result) == {'values_changed'}
    changes = list(result['values_changed'])
    assert len(changes) == 1
    assert changes[0].t1 == 2
    assert changes[0].t2 == 3
    assert changes[0].up.t1 == {key: 1, other_key: 2}
    assert changes[0].up.t2 == {key: 1, other_key: 3}


def test_datetime_key_with_ignored_numeric_value_types():
    """Reproduce issue 550 through the public comparison API."""
    key = datetime(2020, 5, 17, 22, 15)
    assert DeepDiff({key: 10.0}, {key: 10}, ignore_numeric_type_changes=True) == {}
