import math
import re

from deepdiff import DeepDiff
from deepdiff.operator import BaseOperator


class TestOperators:
    def test_custom_operators_prevent_default(self):
        t1 = {
            "coordinates": [
                {"x": 5, "y": 5},
                {"x": 8, "y": 8}
            ]
        }

        t2 = {
            "coordinates": [
                {"x": 6, "y": 6},
                {"x": 88, "y": 88}
            ]
        }

        class L2DistanceDifferWithPreventDefault(BaseOperator):
            def __init__(self, path_regex: str, distance_threshold: float):
                super().__init__(path_regex)
                self.distance_threshold = distance_threshold

            def _l2_distance(self, c1, c2):
                return math.sqrt(
                    (c1["x"] - c2["x"]) ** 2 + (c1["y"] - c2["y"]) ** 2
                )

            def diff(self, level, diff_instance):
                l2_distance = self._l2_distance(level.t1, level.t2)
                if l2_distance > self.distance_threshold:
                    diff_instance.custom_report_result('distance_too_far', level, {
                        "l2_distance": l2_distance
                    })
                #
                return True

        ddiff = DeepDiff(t1, t2, custom_operators=[L2DistanceDifferWithPreventDefault(
            "^root\\['coordinates'\\]\\[\\d+\\]$",
            1
        )])

        expected = {
            'distance_too_far': {
                "root['coordinates'][0]": {'l2_distance': 1.4142135623730951},
                "root['coordinates'][1]": {'l2_distance': 113.13708498984761}
            }
        }
        assert expected == ddiff

    def test_custom_operators_not_prevent_default(self):
        t1 = {
            "coordinates": [
                {"x": 5, "y": 5},
                {"x": 8, "y": 8}
            ]
        }

        t2 = {
            "coordinates": [
                {"x": 6, "y": 6},
                {"x": 88, "y": 88}
            ]
        }

        class L2DistanceDifferWithPreventDefault(BaseOperator):
            def __init__(self, path_regex, distance_threshold):
                super().__init__(path_regex)
                self.distance_threshold = distance_threshold

            def _l2_distance(self, c1, c2):
                return math.sqrt(
                    (c1["x"] - c2["x"]) ** 2 + (c1["y"] - c2["y"]) ** 2
                )

            def diff(self, level, diff_instance):
                l2_distance = self._l2_distance(level.t1, level.t2)
                if l2_distance > self.distance_threshold:
                    diff_instance.custom_report_result('distance_too_far', level, {
                        "l2_distance": l2_distance
                    })
                #
                return False

        ddiff = DeepDiff(t1, t2, custom_operators=[L2DistanceDifferWithPreventDefault(
            "^root\\['coordinates'\\]\\[\\d+\\]$",
            1
        )
        ])
        expected = {
            'values_changed': {
                "root['coordinates'][0]['x']": {'new_value': 6, 'old_value': 5},
                "root['coordinates'][0]['y']": {'new_value': 6, 'old_value': 5},
                "root['coordinates'][1]['x']": {'new_value': 88, 'old_value': 8},
                "root['coordinates'][1]['y']": {'new_value': 88, 'old_value': 8}
            },
            'distance_too_far': {
                "root['coordinates'][0]": {'l2_distance': 1.4142135623730951},
                "root['coordinates'][1]": {'l2_distance': 113.13708498984761}
            }
        }
        assert expected == ddiff

    def test_custom_operators_should_not_equal(self):
        t1 = {
            "id": 5,
            "expect_change_pos": 10,
            "expect_change_neg": 10,
        }

        t2 = {
            "id": 5,
            "expect_change_pos": 100,
            "expect_change_neg": 10,
        }

        class ExpectChangeOperator(BaseOperator):
            def __init__(self, path_regex):
                super().__init__(path_regex)

            def diff(self, level, diff_instance):
                if level.t1 == level.t2:
                    diff_instance.custom_report_result('unexpected:still', level, {
                        "old": level.t1,
                        "new": level.t2
                    })

                return True

        ddiff = DeepDiff(t1, t2, custom_operators=[
            ExpectChangeOperator("root\\['expect_change.*'\\]")
        ])

        assert ddiff == {'unexpected:still': {"root['expect_change_neg']": {'old': 10, 'new': 10}}}
