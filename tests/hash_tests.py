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

    def test_hash_str(self):
        obj = "a"
        expected_result = {id(obj): '48591f1d794734cabf55f96f5a5a72c084f13ac0'}
        result = DeepHash(obj)
        self.assertEqual(result.hashes, expected_result)

    def test_list1(self):
        string1 = "a"
        obj = [string1, 10, 20]
        expected_result = {id(string1): '48591f1d794734cabf55f96f5a5a72c084f13ac0',
                           id(obj): 'list:int:10,int:20,str:48591f1d794734cabf55f96f5a5a72c084f13ac0'}
        result = DeepHash(obj)
        self.assertEqual(result.hashes, expected_result)

    def test_dict1(self):
        string1 = "a"
        obj = {"key1": string1, 1: 10, 2: 20}
        expected_result = {id(string1): '48591f1d794734cabf55f96f5a5a72c084f13ac0',
                           id(obj): 'dict:int:10,int:20,str:48591f1d794734cabf55f96f5a5a72c084f13ac0'}
        result = DeepHash(obj)
        self.assertEqual(result.hashes, expected_result)
