#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
To run the test:
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
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3]}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2]}}
        ddiff = DeepDiff(t1, t2)
        result = {'iterable_item_removed': ["root[4]['b']: [3]"]}
        self.assertEqual(ddiff, result)

    def test_list_difference2(self):
        # Note that it DOES NOT take order into account
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3]}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 3, 2]}}
        ddiff = DeepDiff(t1, t2)
        self.assertEqual(ddiff, {})

    def test_list_that_contains_dictionary(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, {1: 1, 2: 2}]}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, {1: 3}]}}
        ddiff = DeepDiff(t1, t2)
        result = {'dic_item_removed': ["root[4]['b'][2][2]"],
                  'values_changed': ["root[4]['b'][2][1]: 1 ===> 3"]}
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
