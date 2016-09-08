#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
import logging
from tests import CustomClass
from deepdiff.model import DiffLevel, ChildRelationship, DictRelationship, SubscriptableIterableRelationship, AttributeRelationship

logging.disable(logging.CRITICAL)

# NOTE: Some of these tests use eval() on library results. Using eval() is inherently dangerous.
# While this may be somewhat acceptable here due to the fact that we trust our own lib
# it still leaves the theoretical possibility of executing malicious code.


class DictRelationshipTestCase(TestCase):
    def setUp(self):
        self.customkey = CustomClass(13, 37)
        self.d = {42: 'answer', 'vegan': 'for life', self.customkey: 1337}

    def test_numkey(self):
        rel = DictRelationship(self.d, self.d[42], 42)
        self.assertEqual(rel.access_partial(), "[42]")

    def test_strkey(self):
        rel = ChildRelationship.create(DictRelationship, self.d, self.d['vegan'], 'vegan')
        result = rel.access_string("self.d")
        self.assertEqual(result, "self.d['vegan']")
        self.assertEqual(eval(result), 'for life')

    def test_objkey(self):
        rel = DictRelationship(self.d, self.d[self.customkey], self.customkey)
        self.assertIsNone(rel.access_partial())


class ListRelationshipTestCase(TestCase):
    def setUp(self):
        self.custom = CustomClass(13, 37)
        self.l = [1337, 'vegan', self.custom]

    def test_min(self):
        rel = SubscriptableIterableRelationship(self.l, self.l[0], 0)
        result = rel.access_string("self.l")
        self.assertEqual(result, "self.l[0]")
        self.assertEqual(eval(result), 1337)

    def test_max(self):
        rel = ChildRelationship.create(SubscriptableIterableRelationship, self.l, self.custom, 2)
        self.assertEqual(rel.access_partial(), "[2]")


class AttributeRelationshipTestCase(TestCase):
    def setUp(self):
        self.custom = CustomClass(13, 37)

    def test_a(self):
        rel = AttributeRelationship(self.custom, 13, "a")
        result = rel.access_string("self.custom")
        self.assertEqual(result, "self.custom.a")


class DiffLevelTestCase(TestCase):
    def setUp(self):
        # Test data
        self.custom1 = CustomClass(13, 37)
        self.custom2 = CustomClass(313, 37)
        self.t1 = {42: 'answer', 'vegan': 'for life', 1337: self.custom1}
        self.t2 = {42: 'answer', 'vegan': 'for the animals', 1337: self.custom2}

        # Manually build diff, bottom up
        self.lowest = DiffLevel(self.custom1.a, self.custom2.a, report_type='values_changed')

        # Test manual child relationship
        rel_int_low_t1 = AttributeRelationship(self.custom1, self.custom1.a, "a")
        rel_int_low_t2 = AttributeRelationship(self.custom2, self.custom2.a, "a")
        self.intermediate = DiffLevel(self.custom1, self.custom2, down=self.lowest,
                                      child_rel1=rel_int_low_t1, child_rel2=rel_int_low_t2)
        self.lowest.up = self.intermediate

        # Test automatic child relationship
        self.highest = DiffLevel(self.t1, self.t2, down=self.intermediate,
                                 child_rel1=DictRelationship, child_rel2=1337)
        self.intermediate.up = self.highest

    def test_all_up(self):
        self.assertEqual(self.lowest.all_up(), self.highest)

    def test_all_down(self):
        self.assertEqual(self.highest.all_down(), self.lowest)

    def test_automatic_child_rel(self):
        self.assertIsInstance(self.highest.t1_child_rel, DictRelationship)
        self.assertIsInstance(self.highest.t2_child_rel, DictRelationship)

        self.assertEqual(self.highest.t1_child_rel.parent, self.highest.t1)
        self.assertEqual(self.highest.t2_child_rel.parent, self.highest.t2)
        self.assertEqual(self.highest.t1_child_rel.parent, self.highest.t1)
        self.assertEqual(self.highest.t2_child_rel.parent, self.highest.t2)

        # Provides textual relationship from t1 to t1[1337]
        self.assertEqual(self.custom1, eval(self.highest.t2_child_rel.access_string("self.t1")))

    def test_path(self):
        # Provides textual path all the way through
        self.assertEqual(self.lowest.path("self.t1"), "self.t1[1337].a")
