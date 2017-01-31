#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
To run only the search tests:
    python -m unittest tests.test_serialization

Or to run all the tests:
    python -m unittest discover

Or to run all the tests with coverage:
    coverage run --source deepdiff setup.py test

Or using Nose:
    nosetests --with-coverage --cover-package=deepdiff

To run a specific test, run this from the root of repo:
    python -m unittest tests.test_serialization.DeepDiffTextTestCase.test_same_objects

or using nosetests:
    nosetests tests/test_serialization.py:DeepDiffTestCase.test_diff_when_hash_fails
"""
import unittest
from deepdiff import DeepDiff

import logging
logging.disable(logging.CRITICAL)


class DeepAdditionsTestCase(unittest.TestCase):
    """Tests for Additions and Subtractions."""

    def test_serialization_text(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3]}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world\n\n\nEnd"}}
        ddiff = DeepDiff(t1, t2)
        self.assertTrue("deepdiff.helper.RemapDict" in ddiff.json)

    def test_deserialization(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3]}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world\n\n\nEnd"}}
        ddiff = DeepDiff(t1, t2)
        jsoned = ddiff.json
        ddiff2 = DeepDiff.from_json(jsoned)
        self.assertEqual(ddiff, ddiff2)

    def test_serialization_tree(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3]}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world\n\n\nEnd"}}
        ddiff = DeepDiff(t1, t2, view='tree')
        jsoned = ddiff.json
        self.assertTrue("world" in jsoned)

    def test_deserialization_tree(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3]}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world\n\n\nEnd"}}
        ddiff = DeepDiff(t1, t2, view='tree')
        jsoned = ddiff.json
        ddiff2 = DeepDiff.from_json(jsoned)
        self.assertTrue('type_changes' in ddiff2)

    def test_deleting_serialization_cache(self):
        t1 = {1: 1}
        t2 = {1: 2}
        ddiff = DeepDiff(t1, t2)
        self.assertFalse(hasattr(ddiff, '_json'))
        ddiff.json
        self.assertTrue(hasattr(ddiff, '_json'))
        del ddiff.json
        self.assertFalse(hasattr(ddiff, '_json'))
