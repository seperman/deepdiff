#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
import logging
from tests import CustomClass, CustomClassMisleadingRepr
from deepdiff.model import (DiffLevel, ChildRelationship, DictRelationship,
                            SubscriptableIterableRelationship, AttributeRelationship)

logging.disable(logging.CRITICAL)


class DictRelationshipTestCase(TestCase):
    def setUp(self):
        self.customkey = CustomClass(a=13, b=37)
        self.customkey_misleading = CustomClassMisleadingRepr(a=11, b=20)
        self.d = {42: 'answer', 'vegan': 'for life',
                  self.customkey: 1337, self.customkey_misleading: 'banana'}

    def test_numkey(self):
        rel = DictRelationship(parent=self.d, child=self.d[42], param=42)
        self.assertEqual(rel.get_partial(), "[42]")

    def test_strkey(self):
        rel = ChildRelationship.create(klass=DictRelationship, parent=self.d,
                                       child=self.d['vegan'], param='vegan')
        result = rel.get_partial()
        self.assertEqual(result, "['vegan']")

    def test_objkey(self):
        rel = DictRelationship(parent=self.d, child=self.d[self.customkey], param=self.customkey)
        self.assertIsNone(rel.get_partial())

    def test_objkey_misleading_repr(self):
        rel = DictRelationship(parent=self.d, child=self.d[self.customkey_misleading],
                               param=self.customkey_misleading)
        self.assertIsNone(rel.get_partial())


class ListRelationshipTestCase(TestCase):
    def setUp(self):
        self.custom = CustomClass(13, 37)
        self.l = [1337, 'vegan', self.custom]

    def test_min(self):
        rel = SubscriptableIterableRelationship(self.l, self.l[0], 0)
        result = rel.get_partial()
        self.assertEqual(result, "[0]")

    def test_max(self):
        rel = ChildRelationship.create(SubscriptableIterableRelationship, self.l, self.custom, 2)
        self.assertEqual(rel.get_partial(), "[2]")


class AttributeRelationshipTestCase(TestCase):
    def setUp(self):
        self.custom = CustomClass(13, 37)

    def test_a(self):
        rel = AttributeRelationship(self.custom, 13, "a")
        result = rel.get_partial()
        self.assertEqual(result, ".a")


class DiffLevelTestCase(TestCase):
    def setUp(self):
        # Test data
        self.custom1 = CustomClass(a=13, b=37)
        self.custom2 = CustomClass(a=313, b=37)
        self.t1 = {42: 'answer', 'vegan': 'for life', 1337: self.custom1}
        self.t2 = {42: 'answer', 'vegan': 'for the animals', 1337: self.custom2}

        # Manually build diff, bottom up
        self.lowest = DiffLevel(self.custom1.a, self.custom2.a, report_type='values_changed')

        # Test manual child relationship
        rel_int_low_t1 = AttributeRelationship(parent=self.custom1, child=self.custom1.a, param="a")
        rel_int_low_t2 = AttributeRelationship(parent=self.custom2, child=self.custom2.a, param="a")
        self.intermediate = DiffLevel(self.custom1, self.custom2, down=self.lowest,
                                      child_rel1=rel_int_low_t1, child_rel2=rel_int_low_t2)
        self.lowest.up = self.intermediate

        # Test automatic child relationship
        t1_child_rel = ChildRelationship.create(klass=DictRelationship, parent=self.t1,
                                                child=self.intermediate.t1, param=1337)
        t2_child_rel = ChildRelationship.create(klass=DictRelationship, parent=self.t2,
                                                child=self.intermediate.t2, param=1337)
        self.highest = DiffLevel(self.t1, self.t2, down=self.intermediate,
                                 child_rel1=t1_child_rel, child_rel2=t2_child_rel)
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
        self.assertEqual('[1337]', self.highest.t2_child_rel.get_partial())

    def test_path(self):
        # Provides textual path all the way through
        self.assertEqual(self.lowest.path("self.t1"), "self.t1[1337].a")


class ChildRelationshipTestCase(TestCase):
    def test_create_invalid_klass(self):
        with self.assertRaises(TypeError):
            ChildRelationship.create(DiffLevel, "hello", 42)
