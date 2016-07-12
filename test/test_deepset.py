#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
To run the test, run this in the root of repo:
python -m unittest discover

To run a specific test, run this from the root of repo:
python -m unittest tests.DeepDiffTestCase.test_list_of_sets_difference_ignore_order
"""
import unittest
from decimal import Decimal
from sys import version
from copy import copy

from deepdiff.deepset import DeepSet

from . import CustomClass
from . import py3


class DeepSetTestCase(unittest.TestCase):
    def test_eq_same_object(self):
        t1 = DeepSet({"vegan", "for", "life"})
        self.assertEqual(t1, t1)

    def test_eq_copied_object(self):
        t1 = DeepSet({"vegan", "for", "life"})
        t2 = copy(t1)
        self.assertEqual(t1, t2)

    def test_eq_values_added_in_different_order(self):
        t1 = DeepSet({"meat", "is", "murder"})
        t2 = DeepSet({"murder", "is", "meat"})
        self.assertEqual(t1, t2)

    def test_eq_default_set(self):
        t1 = DeepSet({"meat", "is", "murder"})
        t2 = {"meat", "is", "murder"}
        self.assertEqual(t1, t2)

    def test_eq_different_values(self):
        t1 = DeepSet({"vegan", "for", "life"})
        t2 = DeepSet({"meat", "is", "murder"})
        self.assertNotEqual(t1, t2)

    def test_eq_custom_objects(self):
        member1 = CustomClass(13, 37)
        member2 = CustomClass(13, 37)
        t1 = DeepSet({member1})
        t2 = DeepSet({member2})
        self.assertEqual(t1, t2)

    def test_custom_object_in_deepset(self):
        member1 = CustomClass(13, 37)
        member2 = CustomClass(13, 37)
        t1 = DeepSet({member1})
        self.assertTrue(member2 in t1)

    def test_custom_object_not_in_deepset(self):
        member1 = CustomClass(13, 37)
        member2 = CustomClass(13, 38)
        t1 = DeepSet({member1})
        self.assertTrue(member2 not in t1)

    def test_sub_trivial(self):
        fibonacci = DeepSet({1, 2, 3, 5, 8, 13})
        self.assertEqual(fibonacci - fibonacci, {})

    def test_sub_copy(self):
        fibonacci = DeepSet({1, 2, 3, 5, 8, 13})
        fibonacci_copy = copy(fibonacci)
        self.assertEqual(fibonacci - fibonacci_copy, {})

    def test_sub_basic(self):
        fibonacci = DeepSet({1, 2, 3, 5, 8, 13})
        primes =    DeepSet({2, 3, 5, 7, 11, 13})
        self.assertEqual(fibonacci - primes, {1, 8})

    def test_sub_custom_objects(self):
        member1 = CustomClass(13, 37)
        member2 = CustomClass(47, 11)
        member3 = CustomClass(47, 11)
        t1 = DeepSet({member1, member2})
        t2 = DeepSet({member3})
        self.assertEqual(t1 - t2, {member1})

    def test_rsub_basic(self):
        fibonacci = {1, 2, 3, 5, 8, 13}
        primes =    DeepSet({2, 3, 5, 7, 11, 13})
        self.assertEqual(fibonacci - primes, {1, 8})

    def test_diff_basic(self):
        fibonacci = DeepSet({1, 2, 3, 5, 8, 13})
        primes =    DeepSet({2, 3, 5, 7, 11, 13})
        self.assertEqual(fibonacci.diff(primes), {'set_item_added': {'root[11]', 'root[7]'}, 'set_item_removed': {'root[1]', 'root[8]'}})
