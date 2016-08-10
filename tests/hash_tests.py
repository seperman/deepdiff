#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
To run only the search tests:
    python -m unittest tests.hash_tests

Or to run all the tests with coverage:
    coverage run --source deepdiff setup.py test

Or using Nose:
    nosetests --with-coverage --cover-package=deepdiff

To run a specific test, run this from the root of repo:
    nosetests .\tests\hash_tests.py:DeepSearchTestCase.test_string_in_root
"""
import unittest
from deepdiff import DeepHash
from sys import version
import logging
logging.disable(logging.CRITICAL)

py3 = version[0] == '3'


class CustomClass:
    def __init__(self, a, b=None):
        self.a = a
        self.b = b

    def __str__(self):
        return "({}, {})".format(self.a, self.b)

    def __repr__(self):
        return self.__str__()


class DeepHashTestCase(unittest.TestCase):

    """DeepSearch Tests."""

    def test_number_in_list(self):
        obj = ["a", 10, 20]
        expected_result = {}
        result = DeepHash(obj)
        self.assertEqual(result.hashes, expected_result)
