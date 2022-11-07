import datetime

from dateutil.rrule import MONTHLY, rrule

from deepdiff import DeepDiff


class TestDeltaIterables:
    def test_diff_rrules(self):

        d = DeepDiff(
            rrule(freq=MONTHLY, count=5, dtstart=datetime.datetime(2014, 12, 31)),
            rrule(freq=MONTHLY, count=4, dtstart=datetime.datetime(2011, 12, 31)),
        )

        assert d == {
            "values_changed": {
                "root[0]": {
                    "new_value": datetime.datetime(2011, 12, 31, 0, 0),
                    "old_value": datetime.datetime(2014, 12, 31, 0, 0),
                },
                "root[1]": {
                    "new_value": datetime.datetime(2012, 1, 31, 0, 0),
                    "old_value": datetime.datetime(2015, 1, 31, 0, 0),
                },
                "root[2]": {
                    "new_value": datetime.datetime(2012, 3, 31, 0, 0),
                    "old_value": datetime.datetime(2015, 3, 31, 0, 0),
                },
                "root[3]": {
                    "new_value": datetime.datetime(2012, 5, 31, 0, 0),
                    "old_value": datetime.datetime(2015, 5, 31, 0, 0),
                },
            },
            "iterable_item_removed": {"root[4]": datetime.datetime(2015, 7, 31, 0, 0)},
        }
