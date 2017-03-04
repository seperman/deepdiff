#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
To run only the search tests:
    python -m unittest tests.test_diff_tree

Or to run all the tests:
    python -m unittest discover

Or to run all the tests with coverage:
    coverage run --source deepdiff setup.py test

Or using Nose:
    nosetests --with-coverage --cover-package=deepdiff

To run a specific test, run this from the root of repo:
    python -m unittest tests.test_diff_tree.DeepDiffTreeTestCase.test_same_objects
"""
import unittest
from deepdiff import DeepDiff
from deepdiff.helper import pypy3, NotPresentHere
from deepdiff.model import DictRelationship, NonSubscriptableIterableRelationship

import logging
logging.disable(logging.CRITICAL)


class DeepDiffTreeTestCase(unittest.TestCase):
    """DeepDiff Tests."""

    def test_same_objects(self):
        t1 = {1: 1, 2: 2, 3: 3}
        t2 = t1
        ddiff = DeepDiff(t1, t2)
        res = ddiff.tree
        self.assertEqual(res, {})

    def test_significant_digits_signed_zero(self):
        t1 = 0.00001
        t2 = -0.0001
        ddiff = DeepDiff(t1, t2, significant_digits=2)
        res = ddiff.tree
        self.assertEqual(res, {})
        t1 = 1 * 10**-12
        t2 = -1 * 10**-12
        ddiff = DeepDiff(t1, t2, significant_digits=10)
        res = ddiff.tree
        self.assertEqual(res, {})

    def test_item_added_extensive(self):
        t1 = {'one': 1, 'two': 2, 'three': 3, 'four': 4}
        t2 = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'new': 1337}
        ddiff = DeepDiff(t1, t2)
        res = ddiff.tree
        (key, ) = res.keys()
        self.assertEqual(key, 'dictionary_item_added')
        self.assertEqual(len(res['dictionary_item_added']), 1)

        (added1, ) = res['dictionary_item_added']

        # assert added1 DiffLevel chain is valid at all
        self.assertEqual(added1.up.down, added1)
        self.assertIsNone(added1.down)
        self.assertIsNone(added1.up.up)
        self.assertEqual(added1.all_up, added1.up)
        self.assertEqual(added1.up.all_down, added1)
        self.assertEqual(added1.report_type, 'dictionary_item_added')

        # assert DiffLevel chain points to the objects we entered
        self.assertEqual(added1.up.t1, t1)
        self.assertEqual(added1.up.t2, t2)

        self.assertEqual(added1.t1, NotPresentHere)
        self.assertEqual(added1.t2, 1337)

        # assert DiffLevel child relationships are correct
        self.assertIsNone(added1.up.t1_child_rel)
        self.assertIsInstance(added1.up.t2_child_rel, DictRelationship)
        self.assertEqual(added1.up.t2_child_rel.parent, added1.up.t2)
        self.assertEqual(added1.up.t2_child_rel.child, added1.t2)
        self.assertEqual(added1.up.t2_child_rel.param, 'new')

        self.assertEqual(added1.up.path(), "root")
        self.assertEqual(added1.path(), "root['new']")

    def test_item_added_and_removed(self):
        t1 = {'one': 1, 'two': 2, 'three': 3, 'four': 4}
        t2 = {'one': 1, 'two': 4, 'three': 3, 'five': 5, 'six': 6}
        ddiff = DeepDiff(t1, t2, view='tree')
        self.assertEqual(
            set(ddiff.keys()), {
                'dictionary_item_added', 'dictionary_item_removed',
                'values_changed'
            })
        self.assertEqual(len(ddiff['dictionary_item_added']), 2)
        self.assertEqual(len(ddiff['dictionary_item_removed']), 1)

    def test_item_added_and_removed2(self):
        t1 = {2: 2, 4: 4}
        t2 = {2: "b", 5: 5}
        ddiff = DeepDiff(t1, t2, view='tree')
        self.assertEqual(
            set(ddiff.keys()), {
                'dictionary_item_added', 'dictionary_item_removed',
                'type_changes'
            })
        self.assertEqual(len(ddiff['dictionary_item_added']), 1)
        self.assertEqual(len(ddiff['dictionary_item_removed']), 1)

    def test_non_subscriptable_iterable(self):
        t1 = (i for i in [42, 1337, 31337])
        t2 = (i for i in [
            42,
            1337,
        ])
        ddiff = DeepDiff(t1, t2, view='tree')
        (change, ) = ddiff['iterable_item_removed']

        self.assertEqual(set(ddiff.keys()), {'iterable_item_removed'})
        self.assertEqual(len(ddiff['iterable_item_removed']), 1)

        self.assertEqual(change.up.t1, t1)
        self.assertEqual(change.up.t2, t2)
        self.assertEqual(change.report_type, 'iterable_item_removed')
        self.assertEqual(change.t1, 31337)
        self.assertEqual(change.t2, NotPresentHere)

        self.assertIsInstance(change.up.t1_child_rel,
                              NonSubscriptableIterableRelationship)
        self.assertIsNone(change.up.t2_child_rel)

    def test_non_subscriptable_iterable_path(self):
        t1 = (i for i in [42, 1337, 31337])
        t2 = (i for i in [42, 1337, ])
        ddiff = DeepDiff(t1, t2, view='tree')
        (change, ) = ddiff['iterable_item_removed']

        # testing path
        self.assertEqual(change.path(), None)
        self.assertEqual(change.path(force='yes'), 'root(unrepresentable)')
        self.assertEqual(change.path(force='fake'), 'root[2]')

    def test_significant_digits(self):
        ddiff = DeepDiff(
            [0.012, 0.98],
            [0.013, 0.99],
            significant_digits=1,
            view='tree')
        self.assertEqual(ddiff, {})

    def test_significant_digits_with_sets(self):
        ddiff = DeepDiff(
            {0.012, 0.98},
            {0.013, 0.99},
            significant_digits=1,
            view='tree')
        self.assertEqual(ddiff, {})

    def test_significant_digits_with_ignore_order(self):
        ddiff = DeepDiff(
            [0.012, 0.98], [0.013, 0.99],
            significant_digits=1,
            ignore_order=True,
            view='tree')
        self.assertEqual(ddiff, {})

    def test_repr(self):
        t1 = {1, 2, 8}
        t2 = {1, 2, 3, 5}
        ddiff = DeepDiff(t1, t2, view='tree')
        try:
            str(ddiff)
        except Exception as e:
            self.fail("Converting ddiff to string raised: {}".format(e))


class DeepDiffTreeWithNumpyTestCase(unittest.TestCase):
    """DeepDiff Tests with Numpy."""

    def setUp(self):
        if not pypy3:
            import numpy as np
            a1 = np.array([1.23, 1.66, 1.98])
            a2 = np.array([1.23, 1.66, 1.98])
            self.d1 = {'np': a1}
            self.d2 = {'np': a2}

    @unittest.skipIf(pypy3, "Numpy is not compatible with pypy3")
    def test_diff_with_numpy(self):
        ddiff = DeepDiff(self.d1, self.d2)
        res = ddiff.tree
        self.assertEqual(res, {})

    @unittest.skipIf(pypy3, "Numpy is not compatible with pypy3")
    def test_diff_with_empty_seq(self):
        a1 = {"empty": []}
        a2 = {"empty": []}
        ddiff = DeepDiff(a1, a2)
        self.assertEqual(ddiff, {})


class DeepAdditionsTestCase(unittest.TestCase):
    """Tests for Additions and Subtractions."""

    @unittest.expectedFailure
    def test_adding_list_diff(self):
        t1 = [1, 2]
        t2 = [1, 2, 3, 5]
        ddiff = DeepDiff(t1, t2, view='tree')
        addition = ddiff + t1
        self.assertEqual(addition, t2)
