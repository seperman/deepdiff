import math

from typing import List
from deepdiff import DeepDiff
from deepdiff.operator import BaseOperator, PrefixOrSuffixOperator


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
            def __init__(self, regex_paths: List[str], distance_threshold: float):
                super().__init__(regex_paths)
                self.distance_threshold = distance_threshold

            def _l2_distance(self, c1, c2):
                return math.sqrt(
                    (c1["x"] - c2["x"]) ** 2 + (c1["y"] - c2["y"]) ** 2
                )

            def give_up_diffing(self, level, diff_instance):
                l2_distance = self._l2_distance(level.t1, level.t2)
                if l2_distance > self.distance_threshold:
                    diff_instance.custom_report_result('distance_too_far', level, {
                        "l2_distance": l2_distance
                    })
                return True

        ddiff = DeepDiff(t1, t2, custom_operators=[L2DistanceDifferWithPreventDefault(
            ["^root\\['coordinates'\\]\\[\\d+\\]$"],
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
            def __init__(self, regex_paths, distance_threshold):
                super().__init__(regex_paths)
                self.distance_threshold = distance_threshold

            def _l2_distance(self, c1, c2):
                return math.sqrt(
                    (c1["x"] - c2["x"]) ** 2 + (c1["y"] - c2["y"]) ** 2
                )

            def give_up_diffing(self, level, diff_instance):
                l2_distance = self._l2_distance(level.t1, level.t2)
                if l2_distance > self.distance_threshold:
                    diff_instance.custom_report_result('distance_too_far', level, {
                        "l2_distance": l2_distance
                    })
                #
                return False

        ddiff = DeepDiff(t1, t2, custom_operators=[L2DistanceDifferWithPreventDefault(
            ["^root\\['coordinates'\\]\\[\\d+\\]$"],
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
            def __init__(self, regex_paths):
                super().__init__(regex_paths)

            def give_up_diffing(self, level, diff_instance):
                if level.t1 == level.t2:
                    diff_instance.custom_report_result('unexpected:still', level, {
                        "old": level.t1,
                        "new": level.t2
                    })

                return True

        ddiff = DeepDiff(t1, t2, custom_operators=[
            ExpectChangeOperator(regex_paths=["root\\['expect_change.*'\\]"])
        ])

        assert ddiff == {'unexpected:still': {"root['expect_change_neg']": {'old': 10, 'new': 10}}}

    def test_custom_operator2(self):

        class CustomClass:

            def __init__(self, d: dict, l: list):
                self.dict = d
                self.dict['list'] = l

            def __repr__(self):
                return "Class list is " + str(self.dict['list'])

        custom1 = CustomClass(d=dict(a=1, b=2), l=[1, 2, 3])
        custom2 = CustomClass(d=dict(c=3, d=4), l=[1, 2, 3, 2])
        custom3 = CustomClass(d=dict(a=1, b=2), l=[1, 2, 3, 4])

        class ListMatchOperator(BaseOperator):

            def give_up_diffing(self, level, diff_instance):
                if set(level.t1.dict['list']) == set(level.t2.dict['list']):
                    return True

        ddiff = DeepDiff(custom1, custom2, custom_operators=[
            ListMatchOperator(types=[CustomClass])
        ])

        assert {} == ddiff

        ddiff2 = DeepDiff(custom2, custom3, threshold_to_diff_deeper=0, custom_operators=[
            ListMatchOperator(types=[CustomClass])
        ])

        expected = {
            'dictionary_item_added': ["root.dict['a']", "root.dict['b']"],
            'dictionary_item_removed': ["root.dict['c']", "root.dict['d']"],
            'values_changed': {"root.dict['list'][3]": {'new_value': 4, 'old_value': 2}}}

        assert expected == ddiff2

    def test_include_only_certain_path(self):

        class MyOperator:

            def __init__(self, include_paths):
                self.include_paths = include_paths

            def match(self, level) -> bool:
                return True

            def give_up_diffing(self, level, diff_instance) -> bool:
                return level.path() not in self.include_paths

        t1 = {'a': [10, 11], 'b': [20, 21], 'c': [30, 31]}
        t2 = {'a': [10, 22], 'b': [20, 33], 'c': [30, 44]}

        ddiff = DeepDiff(t1, t2, custom_operators=[
            MyOperator(include_paths="root['a'][1]")
        ])

        expected = {'values_changed': {"root['a'][1]": {'new_value': 22, 'old_value': 11}}}
        assert expected == ddiff

    def test_give_up_diffing_on_first_diff(self):

        class MyOperator:

            def match(self, level) -> bool:
                return True

            def give_up_diffing(self, level, diff_instance) -> bool:
                return any(diff_instance.tree.values())

        t1 = [[1, 2], [3, 4], [5, 6]]
        t2 = [[1, 3], [3, 5], [5, 7]]

        ddiff = DeepDiff(t1, t2, custom_operators=[
            MyOperator()
        ])

        expected = {'values_changed': {'root[0][1]': {'new_value': 3, 'old_value': 2}}}
        assert expected == ddiff

    def test_prefix_or_suffix_diff(self):

        t1 = {
            "key1": ["foo", "bar's food", "jack", "joe"]
        }
        t2 = {
            "key1": ["foo", "bar", "jill", "joe'car"]
        }

        ddiff = DeepDiff(t1, t2, custom_operators=[
            PrefixOrSuffixOperator()
        ])

        expected = {'values_changed': {"root['key1'][2]": {'new_value': 'jill', 'old_value': 'jack'}}}
        assert expected == ddiff

        ddiff2 = DeepDiff(t1, t2, ignore_order=True, custom_operators=[
            PrefixOrSuffixOperator()
        ])

        expected2 = {'values_changed': {"root['key1'][2]": {'new_value': 'jill', 'old_value': 'jack'}}}
        assert expected2 == ddiff2

    def test_custom_operator3_small_numbers(self):
        x = [2.0000000000000027, 2.500000000000005, 2.000000000000002, 3.000000000000001]
        y = [2.000000000000003, 2.500000000000005, 2.0000000000000027, 3.0000000000000027]
        result = DeepDiff(x, y)
        expected = {
            'values_changed': {
                'root[0]': {'new_value': 2.000000000000003, 'old_value': 2.0000000000000027},
                'root[2]': {'new_value': 2.0000000000000027, 'old_value': 2.000000000000002},
                'root[3]': {'new_value': 3.0000000000000027, 'old_value': 3.000000000000001}}}
        assert expected == result

        class CustomCompare(BaseOperator):
            def __init__(self, tolerance, types):
                self.tolerance = tolerance
                self.types = types

            def match(self, level) -> bool:
                if type(level.t1) in self.types:
                    return True

            def give_up_diffing(self, level, diff_instance) -> bool:
                relative = abs(abs(level.t1 - level.t2) / level.t1)
                if not max(relative, self.tolerance) == self.tolerance:
                    custom_report = f'relative diff: {relative:.8e}'
                    diff_instance.custom_report_result('diff', level, custom_report)
                return True

        def compare_func(x, y, level):
            return True

        operators = [CustomCompare(types=[float], tolerance=5.5e-5)]
        result2 = DeepDiff(x, y, custom_operators=operators, iterable_compare_func=compare_func)
        assert {} == result2

        result3 = DeepDiff(x, y, custom_operators=operators, zip_ordered_iterables=True)
        assert {} == result3, "We should get the same result as result2 when zip_ordered_iterables is True."
