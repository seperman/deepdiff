#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
To run only the search tests:
    python -m unittest tests.search_tests

Or to run all the tests with coverage:
    coverage run --source deepdiff setup.py test

Or using Nose:
    nosetests --with-coverage --cover-package=deepdiff

To run a specific test, run this from the root of repo:
    nosetests .\tests\search_tests.py:DeepSearchTestCase.test_string_in_root
"""
import unittest
from deepdiff import DeepSearch
import logging
logging.disable(logging.CRITICAL)

item = "somewhere"


class CustomClass:
    def __init__(self, a, b=None):
        self.a = a
        self.b = b

    def __str__(self):
        return "({}, {})".format(self.a, self.b)

    def __repr__(self):
        return self.__str__()


class DeepSearchTestCase(unittest.TestCase):
    """DeepSearch Tests."""

    def test_number_in_list(self):
        obj = ["a", 10, 20]
        item = 10
        result = {"matched_values": {'root[1]'}}
        self.assertEqual(DeepSearch(obj, item, verbose_level=1), result)

    def test_string_in_root(self):
        obj = "long string somewhere"
        result = {"matched_values": {'root'}}
        self.assertEqual(DeepSearch(obj, item, verbose_level=1), result)

    def test_string_in_root_verbose(self):
        obj = "long string somewhere"
        result = {"matched_values": {'root': "long string somewhere"}}
        self.assertEqual(DeepSearch(obj, item, verbose_level=2), result)

    def test_string_in_tuple(self):
        obj = ("long", "string", 0, "somewhere")
        result = {"matched_values": {'root[3]'}}
        self.assertEqual(DeepSearch(obj, item, verbose_level=1), result)

    def test_string_in_list(self):
        obj = ["long", "string", 0, "somewhere"]
        result = {"matched_values": {'root[3]'}}
        self.assertEqual(DeepSearch(obj, item, verbose_level=1), result)

    def test_string_in_list_verbose(self):
        obj = ["long", "string", 0, "somewhere"]
        result = {"matched_values": {'root[3]': "somewhere"}}
        self.assertEqual(DeepSearch(obj, item, verbose_level=2), result)

    def test_string_in_list_verbose2(self):
        obj = ["long", "string", 0, "somewhere great!"]
        result = {"matched_values": {'root[3]': "somewhere great!"}}
        self.assertEqual(DeepSearch(obj, item, verbose_level=2), result)

    def test_string_in_list_verbose3(self):
        obj = ["long somewhere", "string", 0, "somewhere great!"]
        result = {
            "matched_values": {
                'root[0]': 'long somewhere',
                'root[3]': "somewhere great!"
            }
        }
        self.assertEqual(DeepSearch(obj, item, verbose_level=2), result)

    def test_int_in_dictionary(self):
        obj = {"long": "somewhere", "num": 2, 0: 0, "somewhere": "around"}
        item = 2
        result = {'matched_values': {"root['num']"}}
        ds = DeepSearch(obj, item, verbose_level=1)
        self.assertEqual(ds, result)

    def test_string_in_dictionary(self):
        obj = {"long": "somewhere", "string": 2, 0: 0, "somewhere": "around"}
        result = {
            'matched_paths': {"root['somewhere']"},
            'matched_values': {"root['long']"}
        }
        ds = DeepSearch(obj, item, verbose_level=1)
        self.assertEqual(ds, result)

    def test_string_in_dictionary_verbose(self):
        obj = {"long": "somewhere", "string": 2, 0: 0, "somewhere": "around"}
        result = {
            'matched_paths': {
                "root['somewhere']": "around"
            },
            'matched_values': {
                "root['long']": "somewhere"
            }
        }
        ds = DeepSearch(obj, item, verbose_level=2)
        self.assertEqual(ds, result)

    def test_string_in_dictionary_in_list_verbose(self):
        obj = [
            "something somewhere", {
                "long": "somewhere",
                "string": 2,
                0: 0,
                "somewhere": "around"
            }
        ]
        result = {
            'matched_paths': {
                "root[1]['somewhere']": "around"
            },
            'matched_values': {
                "root[1]['long']": "somewhere",
                "root[0]": "something somewhere"
            }
        }
        ds = DeepSearch(obj, item, verbose_level=2)
        self.assertEqual(ds, result)

    def test_custom_object(self):
        obj = CustomClass('here, something', 'somewhere')
        result = {'matched_values': {'root.b'}}
        ds = DeepSearch(obj, item, verbose_level=1)
        self.assertEqual(ds, result)

    def test_custom_object_verbose(self):
        obj = CustomClass('here, something', 'somewhere out there')
        result = {'matched_values': {'root.b': 'somewhere out there'}}
        ds = DeepSearch(obj, item, verbose_level=2)
        self.assertEqual(ds, result)

    def test_custom_object_in_dictionary_verbose(self):
        obj = {1: CustomClass('here, something', 'somewhere out there')}
        result = {'matched_values': {'root[1].b': 'somewhere out there'}}
        ds = DeepSearch(obj, item, verbose_level=2)
        self.assertEqual(ds, result)

    def test_named_tuples_verbose(self):
        from collections import namedtuple
        Point = namedtuple('Point', ['x', 'somewhere_good'])
        obj = Point(x="my keys are somewhere", somewhere_good=22)
        ds = DeepSearch(obj, item, verbose_level=2)
        result = {
            'matched_values': {
                'root.x': 'my keys are somewhere'
            },
            'matched_paths': {
                'root.somewhere_good': 22
            }
        }
        self.assertEqual(ds, result)

    def test_string_in_set_verbose(self):
        obj = {"long", "string", 0, "somewhere"}
        # result = {"matched_values": {'root[3]': "somewhere"}}
        ds = DeepSearch(obj, item, verbose_level=2)
        self.assertEqual(list(ds["matched_values"].values())[0], item)

    def test_loop(self):
        class LoopTest(object):
            def __init__(self, a):
                self.loop = self
                self.a = a

        obj = LoopTest("somewhere around here.")

        ds = DeepSearch(obj, item, verbose_level=1)
        result = {'matched_values': {'root.a'}}
        self.assertEqual(ds, result)

    def test_loop_in_lists(self):
        obj = [1, 2, 'somewhere']
        obj.append(obj)

        ds = DeepSearch(obj, item, verbose_level=1)
        result = {'matched_values': {'root[2]'}}
        self.assertEqual(ds, result)

    def test_skip_path1(self):
        obj = {
            "for life": "vegan",
            "ingredients": ["no meat", "no eggs", "no dairy", "somewhere"]
        }
        ds = DeepSearch(obj, item, exclude_paths={"root['ingredients']"})
        self.assertEqual(ds, {})

    def test_custom_object_skip_path(self):
        obj = CustomClass('here, something', 'somewhere')
        result = {}
        ds = DeepSearch(obj, item, verbose_level=1, exclude_paths=['root.b'])
        self.assertEqual(ds, result)

    def test_skip_list_path(self):
        obj = ['a', 'somewhere']
        ds = DeepSearch(obj, item, exclude_paths=['root[1]'])
        result = {}
        self.assertEqual(ds, result)

    def test_skip_dictionary_path(self):
        obj = {1: {2: "somewhere"}}
        ds = DeepSearch(obj, item, exclude_paths=['root[1][2]'])
        result = {}
        self.assertEqual(ds, result)

    def test_skip_regexp(self):
        obj = [{'a': 1, 'b': "somewhere"}, {'c': 4, 'b': "somewhere"}]
        ds = DeepSearch(obj, item, exclude_regex_paths=["root\[\d+\]"])
        result = {}
        self.assertEqual(ds, result)

    def test_skip_type_str(self):
        obj = "long string somewhere"
        result = {}
        ds = DeepSearch(obj, item, verbose_level=1, exclude_types=[str])
        self.assertEqual(ds, result)

    def test_unknown_parameters(self):
        with self.assertRaises(ValueError):
            DeepSearch(1, 1, wrong_param=2)

    def test_bad_attribute(self):
        class Bad(object):
            __slots__ = ['x', 'y']

            def __getattr__(self, key):
                raise AttributeError("Bad item")

            def __str__(self):
                return "Bad Object"

        obj = Bad()

        ds = DeepSearch(obj, item, verbose_level=1)
        result = {'unprocessed': ['root']}
        self.assertEqual(ds, result)
        ds = DeepSearch(obj, item, verbose_level=2)
        self.assertEqual(ds, result)
