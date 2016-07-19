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

    def test_eq_ne_custom_object_different_elem_count(self):
        member1a = CustomClass(13, 37)
        member1b = CustomClass(13, 37)
        member2a = CustomClass(47, 11)
        member2b = CustomClass(47, 11)
        t1 = DeepSet(member1a, member2a)
        t2 = DeepSet(member1b)
        t3 = DeepSet(member1a)
        t4 = DeepSet(member1b, member2a)

        self.assertTrue(t2 == t3)
        self.assertFalse(t2 != t3)

        self.assertTrue(t1 != t2)
        self.assertFalse(t1 == t2)

        self.assertTrue(t3 != t1)
        self.assertFalse(t3 == t1)

        self.assertTrue(t4 == t1)
        self.assertFalse(t4 != t1)


    def test_ne_custom_object(self):
        member1 = CustomClass(13, 37)
        member2 = CustomClass(13, 37)
        t1 = DeepSet({member1})
        t2 = DeepSet({member2})
        self.assertFalse(t1 != t2)



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



    def test_disjoint_basic_true(self):
        t1 = DeepSet({"vegan", "for", "life"})
        t2 = DeepSet({"meat", "is", "murder"})
        self.assertTrue(t1.isdisjoint(t2))

    def test_disjoint_basic_false(self):
        fibonacci = DeepSet({1, 2, 3, 5, 8, 13})
        primes =    DeepSet({2, 3, 5, 7, 11, 13})
        self.assertFalse(fibonacci.isdisjoint(primes))

    def test_disjoint_custom_objects_true(self):
        member1 = CustomClass(13, 37)
        member2 = CustomClass(14, 37)
        t1 = DeepSet({member1})
        t2 = DeepSet({member2})
        self.assertTrue(t1.isdisjoint(t2))

    def test_disjoint_custom_objects_false(self):
        member1 = CustomClass(13, 37)
        member2 = CustomClass(13, 37)
        t1 = DeepSet({member1})
        t2 = DeepSet({member2})
        self.assertFalse(t1.isdisjoint(t2))



    # issubset(), <=, <

    def test_issubset_basic(self):
        fibonacci    = DeepSet({1, 2, 3, 5, 8, 13})
        first_primes = DeepSet({2, 3, 5})
        self.assertTrue(first_primes.issubset(fibonacci))
        self.assertTrue(first_primes <= fibonacci)

        fibonacci = DeepSet({1, 2, 3, 5, 8, 13})
        primes = DeepSet({2, 3, 5, 7, 11, 13})
        self.assertFalse(primes.issubset(fibonacci))
        self.assertFalse(primes <= fibonacci)

    def test_issubset_custom_objects(self):
        member1a = CustomClass(13, 37)
        member1b = CustomClass(13, 37)
        member2a = CustomClass(47, 11)
        member2b = CustomClass(47, 11)

        t1 = DeepSet(member1a, member2a)
        t2 = DeepSet(member1b, member2b)
        t3 = DeepSet(member1b)

        self.assertTrue(t2.issubset(t1))
        self.assertTrue(t2 <= t1)
        self.assertFalse(t2 < t1)

        self.assertTrue(t3.issubset(t1))
        self.assertTrue(t3 <= t1)
        self.assertTrue(t3 < t1)



    # intersection, operator &

    def test_intersection_basic(self):
        fibonacci = DeepSet({1, 2, 3, 5, 8, 13})
        primes =    DeepSet({2, 3, 5, 7, 11, 13})
        self.assertEqual(fibonacci & primes, {2, 3, 5, 13})
        self.assertEqual(primes & fibonacci, {2, 3, 5, 13})

    def test_intersection_custom_objects(self):
        member1a = CustomClass(13, 37)
        member1b = CustomClass(13, 37)
        member2 = CustomClass(8, 15)
        member3 = CustomClass(47, 11)
        t1 = DeepSet({member1a, member2})
        t2 = DeepSet({member1b, member2})
        t3 = DeepSet({member2, member3})
        self.assertEqual(t1.intersection(t2), {member1a, member2})
        self.assertEqual(t1 & t2, {member1a, member2})
        self.assertEqual(t1 & t3, {member2})
        self.assertEqual(t2 & t3, {member2})



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



    def test_remove_basic_good(self):
        fibonacci = DeepSet({1, 2, 3, 5, 8, 13})
        fibonacci.remove(13)
        self.assertEqual(fibonacci, {1, 2, 3, 5, 8})

    def test_remove_basic_error(self):
        fibonacci = DeepSet({1, 2, 3, 5, 8, 13})
        with self.assertRaises(KeyError):
            fibonacci.remove(14)
        self.assertEqual(fibonacci, {1, 2, 3, 5, 8, 13})

    def test_remove_custom_object(self):
        member1 = CustomClass(13, 37)
        member2 = CustomClass(13, 37)
        t1 = DeepSet({member1})
        t1.remove(member2)
        self.assertEqual(t1, {})



    def test_discard_basic_good(self):
        fibonacci = DeepSet({1, 2, 3, 5, 8, 13})
        fibonacci.discard(13)
        self.assertEqual(fibonacci, {1, 2, 3, 5, 8})

    def test_discard_basic_error(self):
        fibonacci = DeepSet({1, 2, 3, 5, 8, 13})
        fibonacci.discard(14)
        self.assertEqual(fibonacci, {1, 2, 3, 5, 8, 13})


    def test_diff_basic(self):
        fibonacci = DeepSet({1, 2, 3, 5, 8, 13})
        primes =    DeepSet({2, 3, 5, 7, 11, 13})
        self.assertEqual(fibonacci.diff(primes), {'set_item_added': {'root[11]', 'root[7]'}, 'set_item_removed': {'root[1]', 'root[8]'}})
