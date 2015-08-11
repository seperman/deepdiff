#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
To run the test, run this in the root of repo:
python -m unittest discover
"""

import unittest

from deepdiff import DeepDiff


class DeepDiffTestCase(unittest.TestCase):

    def test_same_objects(self):
        t1 = {1: 1, 2: 2, 3: 3}
        t2 = t1
        self.assertEqual(DeepDiff(t1, t2), {})

    def test_item_change(self):
        t1 = {1: 1, 2: 2, 3: 3}
        t2 = {1: 1, 2: "2", 3: 3}
        self.assertEqual(DeepDiff(t1, t2), {'type_changes': ["root[2]: 2=<type 'int'> ===> 2=<type 'str'>"]})

    def test_value_change(self):
        t1 = {1: 1, 2: 2, 3: 3}
        t2 = {1: 1, 2: 4, 3: 3}
        self.assertEqual(DeepDiff(t1, t2), {'values_changed': ['root[2]: 2 ===> 4']})

    def test_item_added_and_removed(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: 4}
        t2 = {1: 1, 2: 4, 3: 3, 5: 5, 6: 6}
        ddiff = DeepDiff(t1, t2)
        result = {'dic_item_added': ['root[5, 6]'], 'dic_item_removed': [
            'root[4]'], 'values_changed': ['root[2]: 2 ===> 4']}
        self.assertEqual(ddiff, result)

    def test_string_difference(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world"}}
        t2 = {1: 1, 2: 4, 3: 3, 4: {"a": "hello", "b": "world!"}}
        ddiff = DeepDiff(t1, t2)
        result = {'values_changed': ['root[2]: 2 ===> 4',
                                     "root[4]['b']: 'world' ===> 'world!'"]}
        self.assertEqual(ddiff, result)

    def test_string_difference2(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world!\nGoodbye!\n1\n2\nEnd"}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world\n1\n2\nEnd"}}
        ddiff = DeepDiff(t1, t2)
        result = {'values_changed': ["root[4]['b']:\n"
                                     '--- \n'
                                     '+++ \n'
                                     '@@ -1,5 +1,4 @@\n'
                                     '-world!\n'
                                     '-Goodbye!\n'
                                     '+world\n'
                                     ' 1\n'
                                     ' 2\n'
                                     ' End']}
        self.assertEqual(ddiff, result)

    def test_type_change(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3]}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world\n\n\nEnd"}}
        ddiff = DeepDiff(t1, t2)
        result = {'type_changes': ["root[4]['b']: [1, 2, 3]=<type 'list'> ===> world\n"
                                   '\n'
                                   '\n'
                                   "End=<type 'str'>"]}
        self.assertEqual(ddiff, result)

    def test_list_difference(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 'to_be_removed', 'to_be_removed2']}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2]}}
        ddiff = DeepDiff(t1, t2)
        result = {'iterable_item_removed': ["root[4]['b']: ['to_be_removed', 'to_be_removed2']"]}
        self.assertEqual(ddiff, result)

    def test_list_difference_add(self):
        t1 = [1, 2]
        t2 = [1, 2, 3, 5]
        ddiff = DeepDiff(t1, t2)
        result = {'iterable_item_added': ["root: [3, 5]"]}
        self.assertEqual(ddiff, result)

    def test_list_difference2(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3, 3, 4]}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 3, 2]}}
        ddiff = DeepDiff(t1, t2)
        self.assertEqual(ddiff, {'values_changed': [
                         "root[4]['b'][1]: 2 ===> 3", "root[4]['b'][2]: 3 ===> 2"],
                         'iterable_item_removed': ["root[4]['b']: [3, 4]"]})

    def test_list_difference3(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3]}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 3, 2, 3]}}
        ddiff = DeepDiff(t1, t2)
        self.assertEqual(ddiff, {'values_changed': [
                         "root[4]['b'][1]: 2 ===> 3", "root[4]['b'][2]: 3 ===> 2"],
                         'iterable_item_added': ["root[4]['b']: [3]"]})

    def test_list_difference_ignore_order(self):
        t1 = {1: 1, 4: {"a": "hello", "b": [1, 2, 3]}}
        t2 = {1: 1, 4: {"a": "hello", "b": [1, 3, 2, 3]}}
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        self.assertEqual(ddiff, {})

    def test_list_that_contains_dictionary(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, {1: 1, 2: 2}]}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, {1: 3}]}}
        ddiff = DeepDiff(t1, t2)
        result = {'dic_item_removed': ["root[4]['b'][2][2]"],
                  'values_changed': ["root[4]['b'][2][1]: 1 ===> 3"]}
        self.assertEqual(ddiff, result)

    def test_set(self):
        t1 = {1, 2, 8}
        t2 = {1, 2, 3, 5}
        ddiff = DeepDiff(t1, t2)
        result = {'set_item_added': ["root: [3, 5]"], 'set_item_removed': ["root: [8]"]}
        self.assertEqual(ddiff, result)

    def test_frozenset(self):
        t1 = frozenset([1, 2, 8])
        t2 = frozenset([1, 2, 3, 5])
        ddiff = DeepDiff(t1, t2)
        result = {'set_item_added': ["root: [3, 5]"], 'set_item_removed': ["root: [8]"]}
        self.assertEqual(ddiff, result)

    def test_tuple(self):
        t1 = (1, 2, 8)
        t2 = (1, 2, 3, 5)
        ddiff = DeepDiff(t1, t2)
        result = {'values_changed': ['root[2]: 8 ===> 3'], 'iterable_item_added': ['root: [5]']}
        self.assertEqual(ddiff, result)

    def test_named_tuples(self):
        from collections import namedtuple
        Point = namedtuple('Point', ['x', 'y'])
        t1 = Point(x=11, y=22)
        t2 = Point(x=11, y=23)
        ddiff = DeepDiff(t1, t2)
        result = {'values_changed': ['root.y: 22 ===> 23']}
        self.assertEqual(ddiff, result)

    def test_custom_objects_change(self):
        class ClassA(object):
            a = 1

            def __init__(self, b):
                self.b = b

        t1 = ClassA(1)
        t2 = ClassA(2)
        ddiff = DeepDiff(t1, t2)
        result = {'values_changed': ['root.b: 1 ===> 2']}
        self.assertEqual(ddiff, result)

    def test_custom_objects_slot_change(self):
        class ClassA(object):
            __slots__ = ['x', 'y']

            def __init__(self, x, y):
                self.x = x
                self.y = y

        t1 = ClassA(1, 1)
        t2 = ClassA(1, 2)
        ddiff = DeepDiff(t1, t2)
        result = {'values_changed': ['root.y: 1 ===> 2']}
        self.assertEqual(ddiff, result)

    def test_custom_objects_add(self):
        class ClassA(object):
            a = 1

            def __init__(self, b):
                self.b = b

        t1 = ClassA(1)
        t2 = ClassA(2)
        t2.c = "new attribute"
        ddiff = DeepDiff(t1, t2)
        result = {'attribute_added': ['root.c'], 'values_changed': ['root.b: 1 ===> 2']}
        self.assertEqual(ddiff, result)

    def test_loop(self):
        class LoopTest(object):
            def __init__(self, a):
                self.loop = self
                self.a = a

        t1 = LoopTest(1)
        t2 = LoopTest(2)

        ddiff = DeepDiff(t1, t2)
        result = {'values_changed': ['root.a: 1 ===> 2']}
        self.assertEqual(ddiff, result)

    def test_loop2(self):
        class LoopTestA(object):
            def __init__(self, a):
                self.loop = LoopTestB
                self.a = a

        class LoopTestB(object):
            def __init__(self, a):
                self.loop = LoopTestA
                self.a = a

        t1 = LoopTestA(1)
        t2 = LoopTestA(2)

        ddiff = DeepDiff(t1, t2)
        result = {'values_changed': ['root.a: 1 ===> 2']}
        self.assertEqual(ddiff, result)

    def test_loop3(self):
        class LoopTest(object):
            def __init__(self, a):
                self.loop = LoopTest
                self.a = a

        t1 = LoopTest(1)
        t2 = LoopTest(2)

        ddiff = DeepDiff(t1, t2)
        result = {'values_changed': ['root.a: 1 ===> 2']}
        self.assertEqual(ddiff, result)
