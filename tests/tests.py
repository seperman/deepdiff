#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
To run the test, run this in the root of repo:
python -m unittest discover
"""
# from __future__ import unicode_literals
import unittest
from decimal import Decimal
from sys import version
py3 = version[0] == '3'

from deepdiff import DeepDiff

from sys import version
py3 = version[0] == '3'


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

    def test_list_of_unhashable_difference_ignore_order(self):
        t1 = [{"a": 2}, {"b": [3, 4, {1: 1}]}]
        t2 = [{"b": [3, 4, {1: 1}]}, {"a": 2}]
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

    def test_decimal(self):
        t1 = {1: Decimal('10.1')}
        t2 = {1: Decimal('2.2')}
        ddiff = DeepDiff(t1, t2)
        result = {'values_changed': ['root[1]: 10.1 ===> 2.2']}
        self.assertEqual(ddiff, result)

    def test_decimal_ignore_order(self):
        t1 = [{1: Decimal('10.1')}, {2: Decimal('10.2')}]
        t2 = [{2: Decimal('10.2')}, {1: Decimal('10.1')}]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        result = {}
        self.assertEqual(ddiff, result)

    def test_unicode_string_type_changes(self):
        unicodeString = {"hello": u"你好"}
        asciiString = {"hello": "你好"}
        ddiff = DeepDiff(unicodeString, asciiString)
        if py3:
            # In python3, all string is unicode, so diff is empty
            result = {}
        else:
            # In python2, these are 2 different type of strings
            result = {'type_changes': [u"root['hello']: \u4f60\u597d=<type 'unicode'> ===> \u4f60\u597d=<type 'str'>"]}
        self.assertEqual(ddiff, result)

    def test_unicode_string_value_changes(self):
        unicodeString = {"hello": u"你好"}
        asciiString = {"hello": u"你好hello"}
        ddiff = DeepDiff(unicodeString, asciiString)
        if py3:
            result = {'values_changed': ["root['hello']: '你好' ===> '你好hello'"]}
        else:
            result = {'values_changed': [u"root['hello']: '\u4f60\u597d' ===> '\u4f60\u597dhello'"]}
        self.assertEqual(ddiff, result)

    def test_unicode_string_value_and_type_changes(self):
        unicodeString = {"hello": u"你好"}
        asciiString = {"hello": "你好hello"}
        ddiff = DeepDiff(unicodeString, asciiString)
        if py3:
            # In python3, all string is unicode, so these 2 strings only diff in values
            result = {'values_changed': ["root['hello']: '你好' ===> '你好hello'"]}
        else:
            # In python2, these are 2 different type of strings
            result = {'type_changes': [u"root['hello']: \u4f60\u597d=<type 'unicode'> ===> \u4f60\u597dhello=<type 'str'>"]}
        self.assertEqual(ddiff, result)

    def test_int_to_unicode_string(self):
        t1 = 1
        asciiString = "你好"
        ddiff = DeepDiff(t1, asciiString)
        if py3:
            # In python3, all string is unicode, so these 2 strings only diff in values
            result = {'type_changes': ["root: 1=<type 'int'> ===> 你好=<type 'str'>"]}
        else:
            # In python2, these are 2 different type of strings
            result = {'type_changes': [u"root: 1=<type 'int'> ===> \u4f60\u597d=<type 'str'>"]}
        self.assertEqual(ddiff, result)

    def test_int_to_unicode(self):
        t1 = 1
        unicodeString = u"你好"
        ddiff = DeepDiff(t1, unicodeString)
        if py3:
            # In python3, all string is unicode, so these 2 strings only diff in values
            result = {'type_changes': ["root: 1=<type 'int'> ===> 你好=<type 'str'>"]}
        else:
            # In python2, these are 2 different type of strings
            result = {'type_changes': [u"root: 1=<type 'int'> ===> \u4f60\u597d=<type 'unicode'>"]}
        self.assertEqual(ddiff, result)

    def test_unicode_string_value_and_type_not_changes(self):
        unicodeString = {"hello": u"你好"}
        asciiString = {"hello": u"你好"}
        ddiff = DeepDiff(unicodeString, asciiString)
        result = {}
        self.assertEqual(ddiff, result)

