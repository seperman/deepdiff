#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
To run the test, run this in the root of repo:
    python -m unittest discover

Or to run it with coverage:
    coverage run --source deepdiff setup.py test

Or using Nose:
    nosetests --with-coverage --cover-package=deepdiff

To run a specific test, run this from the root of repo:
    nosetests .\tests\search_tests.py:DeepSearchTestCase.test_string_in_root
"""
import unittest
from deepdiff import DeepSearch
from sys import version
import logging
logging.disable(logging.CRITICAL)

py3 = version[0] == '3'


class DeepSearchTestCase(unittest.TestCase):

    """DeepSearch Tests."""

    def test_string_in_root(self):
        obj = "long string somewhere"
        item = "somewhere"
        result = {"matched_values": {'root'}}
        self.assertEqual(DeepSearch(obj, item, verbose_level=1), result)

    def test_string_in_root_verbose(self):
        obj = "long string somewhere"
        item = "somewhere"
        result = {"matched_values": {'root': "long string somewhere"}}
        self.assertEqual(DeepSearch(obj, item, verbose_level=2), result)

    def test_string_in_list(self):
        obj = ["long", "string", 0, "somewhere"]
        item = "somewhere"
        result = {"matched_values": {'root[3]'}}
        self.assertEqual(DeepSearch(obj, item, verbose_level=1), result)

    def test_string_in_list_verbose(self):
        obj = ["long", "string", 0, "somewhere"]
        item = "somewhere"
        result = {"matched_values": {'root[3]': "somewhere"}}
        self.assertEqual(DeepSearch(obj, item, verbose_level=2), result)

    def test_string_in_list_verbose2(self):
        obj = ["long", "string", 0, "somewhere great!"]
        item = "somewhere"
        result = {"matched_values": {'root[3]': "somewhere great!"}}
        self.assertEqual(DeepSearch(obj, item, verbose_level=2), result)

    def test_string_in_list_verbose3(self):
        obj = ["long somewhere", "string", 0, "somewhere great!"]
        item = "somewhere"
        result = {"matched_values": {'root[0]': 'long somewhere', 'root[3]': "somewhere great!"}}
        self.assertEqual(DeepSearch(obj, item, verbose_level=2), result)
