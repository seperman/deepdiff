#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
To run the test, run this in the root of repo:
python -m unittest discover
"""
import unittest
from decimal import Decimal
from deepdiff import DeepDiff
from sys import version

py3 = version[0] == '3'


class DeepDiffTestCase(unittest.TestCase):

    """DeepDiff Tests."""

    def test_same_objects(self):
        t1 = {1: 1, 2: 2, 3: 3}
        t2 = t1
        self.assertEqual(DeepDiff(t1, t2), {})

    def test_item_change(self):
        t1 = {1: 1, 2: 2, 3: 3}
        t2 = {1: 1, 2: "2", 3: 3}
        self.assertEqual(DeepDiff(t1, t2), {'type_changes': {"root[2]":
                                            {"oldvalue": 2, "oldtype": int,
                                             "newvalue": "2", "newtype": str}}})

    def test_value_change(self):
        t1 = {1: 1, 2: 2, 3: 3}
        t2 = {1: 1, 2: 4, 3: 3}
        result = {'values_changed': {'root[2]': {"oldvalue": 2, "newvalue": 4}}}
        self.assertEqual(DeepDiff(t1, t2), result)

    def test_item_added_and_removed(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: 4}
        t2 = {1: 1, 2: 4, 3: 3, 5: 5, 6: 6}
        ddiff = DeepDiff(t1, t2)
        result = {'dic_item_added': ['root[5]', 'root[6]'], 'dic_item_removed': [
            'root[4]'], 'values_changed': {'root[2]': {"oldvalue": 2, "newvalue": 4}}}
        self.assertEqual(ddiff, result)

    def test_string_difference(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world"}}
        t2 = {1: 1, 2: 4, 3: 3, 4: {"a": "hello", "b": "world!"}}
        ddiff = DeepDiff(t1, t2)
        result = {'values_changed': {'root[2]': {'oldvalue': 2, 'newvalue': 4},
                                     "root[4]['b']": {'oldvalue': 'world', 'newvalue': 'world!'}}}
        self.assertEqual(ddiff, result)

    def test_string_difference2(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world!\nGoodbye!\n1\n2\nEnd"}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world\n1\n2\nEnd"}}
        ddiff = DeepDiff(t1, t2)
        result = {'values_changed': {"root[4]['b']": {
            'diff': '--- \n+++ \n@@ -1,5 +1,4 @@\n-world!\n-Goodbye!\n+world\n 1\n 2\n End',
            'newvalue': 'world\n1\n2\nEnd', 'oldvalue': 'world!\nGoodbye!\n1\n2\nEnd'}}}
        self.assertEqual(ddiff, result)

    def test_type_change(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3]}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world\n\n\nEnd"}}
        ddiff = DeepDiff(t1, t2)
        result = {'type_changes': {"root[4]['b']": {'oldtype': list,
                  'newvalue': 'world\n\n\nEnd', 'oldvalue': [1, 2, 3], 'newtype': str}}}
        self.assertEqual(ddiff, result)

    def test_list_difference(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 'to_be_removed', 'to_be_removed2']}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2]}}
        ddiff = DeepDiff(t1, t2)
        result = {'iterable_item_removed': {"root[4]['b'][2]": "to_be_removed", "root[4]['b'][3]": 'to_be_removed2'}}
        self.assertEqual(ddiff, result)

    def test_list_difference_add(self):
        t1 = [1, 2]
        t2 = [1, 2, 3, 5]
        ddiff = DeepDiff(t1, t2)
        result = {'iterable_item_added': {'root[2]': 3, 'root[3]': 5}}
        self.assertEqual(ddiff, result)

    def test_list_difference2(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3, 10, 12]}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 3, 2]}}
        result = {'values_changed': {"root[4]['b'][2]": {'newvalue': 2, 'oldvalue': 3},
                  "root[4]['b'][1]": {'newvalue': 3, 'oldvalue': 2}},
                  'iterable_item_removed': {"root[4]['b'][3]": 10, "root[4]['b'][4]": 12}}
        ddiff = DeepDiff(t1, t2)
        self.assertEqual(ddiff, result)

    def test_list_difference3(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 5]}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 3, 2, 5]}}
        ddiff = DeepDiff(t1, t2)
        result = {'values_changed': {"root[4]['b'][2]": {'newvalue': 2, 'oldvalue': 5}, "root[4]['b'][1]": {
            'newvalue': 3, 'oldvalue': 2}}, 'iterable_item_added': {"root[4]['b'][3]": 5}}
        self.assertEqual(ddiff, result)

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

    def test_list_of_unhashable_difference_ignore_order2(self):
        t1 = [1, {"a": 2}, {"b": [3, 4, {1: 1}]}, "B"]
        t2 = [{"b": [3, 4, {1: 1}]}, {"a": 2}, {1: 1}]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        result = {'iterable_item_added': {'root[2]': {1: 1}},
                  'iterable_item_removed': {'root[3]': 'B', 'root[0]': 1}}
        self.assertEqual(ddiff, result)

    def test_list_that_contains_dictionary(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, {1: 1, 2: 2}]}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, {1: 3}]}}
        ddiff = DeepDiff(t1, t2)
        result = {'dic_item_removed': ["root[4]['b'][2][2]"],
                  'values_changed': {"root[4]['b'][2][1]": {'oldvalue': 1, 'newvalue': 3}}}
        self.assertEqual(ddiff, result)

    def test_set(self):
        t1 = {1, 2, 8}
        t2 = {1, 2, 3, 5}
        ddiff = DeepDiff(t1, t2)
        result = {'set_item_added': ['root[3]', 'root[5]'], 'set_item_removed': ['root[8]']}
        self.assertEqual(ddiff, result)

    def test_frozenset(self):
        t1 = frozenset([1, 2, 'B'])
        t2 = frozenset([1, 2, 3, 5])
        ddiff = DeepDiff(t1, t2)
        result = {'set_item_added': ['root[3]', 'root[5]'], 'set_item_removed': ["root['B']"]}
        self.assertEqual(ddiff, result)

    def test_tuple(self):
        t1 = (1, 2, 8)
        t2 = (1, 2, 3, 5)
        ddiff = DeepDiff(t1, t2)
        result = {'values_changed': {'root[2]': {'oldvalue': 8, 'newvalue': 3}},
                  'iterable_item_added': {'root[3]': 5}}
        self.assertEqual(ddiff, result)

    def test_named_tuples(self):
        from collections import namedtuple
        Point = namedtuple('Point', ['x', 'y'])
        t1 = Point(x=11, y=22)
        t2 = Point(x=11, y=23)
        ddiff = DeepDiff(t1, t2)
        result = {'values_changed': {'root.y': {'oldvalue': 22, 'newvalue': 23}}}
        self.assertEqual(ddiff, result)

    def test_custom_objects_change(self):
        class ClassA(object):
            a = 1

            def __init__(self, b):
                self.b = b

        t1 = ClassA(1)
        t2 = ClassA(2)
        ddiff = DeepDiff(t1, t2)
        result = {'values_changed': {'root.b': {'oldvalue': 1, 'newvalue': 2}}}
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
        result = {'values_changed': {'root.y': {'oldvalue': 1, 'newvalue': 2}}}
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
        result = {'attribute_added': ["root.'c'"], 'values_changed':
                  {'root.b': {'newvalue': 2, 'oldvalue': 1}}}
        self.assertEqual(ddiff, result)

    def test_loop(self):
        class LoopTest(object):
            def __init__(self, a):
                self.loop = self
                self.a = a

        t1 = LoopTest(1)
        t2 = LoopTest(2)

        ddiff = DeepDiff(t1, t2)
        result = {'values_changed': {'root.a': {'oldvalue': 1, 'newvalue': 2}}}
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
        result = {'values_changed': {'root.a': {'oldvalue': 1, 'newvalue': 2}}}
        self.assertEqual(ddiff, result)

    def test_loop3(self):
        class LoopTest(object):
            def __init__(self, a):
                self.loop = LoopTest
                self.a = a

        t1 = LoopTest(1)
        t2 = LoopTest(2)

        ddiff = DeepDiff(t1, t2)
        result = {'values_changed': {'root.a': {'oldvalue': 1, 'newvalue': 2}}}
        self.assertEqual(ddiff, result)

    def test_decimal(self):
        t1 = {1: Decimal('10.1')}
        t2 = {1: Decimal('2.2')}
        ddiff = DeepDiff(t1, t2)
        result = {'values_changed': {'root[1]': {'newvalue': Decimal('2.2'),
                  'oldvalue': Decimal('10.1')}}}
        self.assertEqual(ddiff, result)

    def test_decimal_ignore_order(self):
        t1 = [{1: Decimal('10.1')}, {2: Decimal('10.2')}]
        t2 = [{2: Decimal('10.2')}, {1: Decimal('10.1')}]
        ddiff = DeepDiff(t1, t2, ignore_order=True)
        result = {}
        self.assertEqual(ddiff, result)

    def test_unicode_string_type_changes(self):
        unicode_string = {"hello": u"你好"}
        ascii_string = {"hello": "你好"}
        ddiff = DeepDiff(unicode_string, ascii_string)
        if py3:
            # In python3, all string is unicode, so diff is empty
            result = {}
        else:
            # In python2, these are 2 different type of strings
            result = {'type_changes': {"root['hello']": {
                      'oldtype': unicode,
                      'newvalue': '\xe4\xbd\xa0\xe5\xa5\xbd',
                      'oldvalue': u'\u4f60\u597d',
                      'newtype': str}}}
        self.assertEqual(ddiff, result)

    # def test_unicode_string_value_changes(self):
    #     unicode_string = {"hello": u"你好"}
    #     ascii_string = {"hello": u"你好hello"}
    #     ddiff = DeepDiff(unicode_string, ascii_string)
    #     if py3:
    #         result = {'values_changed': ["root['hello']: '你好' ===> '你好hello'"]}
    #     else:
    #         result = {'values_changed': [u"root['hello']: '\u4f60\u597d' ===> '\u4f60\u597dhello'"]}
    #     self.assertEqual(ddiff, result)

    # def test_unicode_string_value_and_type_changes(self):
    #     unicode_string = {"hello": u"你好"}
    #     ascii_string = {"hello": "你好hello"}
    #     ddiff = DeepDiff(unicode_string, ascii_string)
    #     if py3:
    #         # In python3, all string is unicode, so these 2 strings only diff in values
    #         result = {'values_changed': ["root['hello']: '你好' ===> '你好hello'"]}
    #     else:
    #         # In python2, these are 2 different type of strings
    #         result = {'type_changes': [u"root['hello']: \u4f60\u597d=<type 'unicode'> ===> \u4f60\u597dhello=<type 'str'>"]}
    #     self.assertEqual(ddiff, result)

    # def test_int_to_unicode_string(self):
    #     t1 = 1
    #     ascii_string = "你好"
    #     ddiff = DeepDiff(t1, ascii_string)
    #     if py3:
    #         # In python3, all string is unicode, so these 2 strings only diff in values
    #         result = {'type_changes': ["root: 1=<type 'int'> ===> 你好=<type 'str'>"]}
    #     else:
    #         # In python2, these are 2 different type of strings
    #         result = {'type_changes': ["root: 1=<type 'int'> ===> \xe4\xbd\xa0\xe5\xa5\xbd=<type 'str'>"]}
    #     self.assertEqual(ddiff, result)

    # def test_int_to_unicode(self):
    #     t1 = 1
    #     unicode_string = u"你好"
    #     ddiff = DeepDiff(t1, unicode_string)
    #     if py3:
    #         # In python3, all string is unicode, so these 2 strings only diff in values
    #         result = {'type_changes': ["root: 1=<type 'int'> ===> 你好=<type 'str'>"]}
    #     else:
    #         # In python2, these are 2 different type of strings
    #         result = {'type_changes': [u"root: 1=<type 'int'> ===> \u4f60\u597d=<type 'unicode'>"]}
    #     self.assertEqual(ddiff, result)

    # def test_unicode_string_value_and_type_not_changes(self):
    #     unicode_string = {"hello": u"你好"}
    #     ascii_string = {"hello": u"你好"}
    #     ddiff = DeepDiff(unicode_string, ascii_string)
    #     result = {}
    #     self.assertEqual(ddiff, result)

    # def test_percent_in_string_type_change(self):
    #     t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "50%"}}
    #     t2 = {1: 1, 2: 4, 3: 3, 4: {"a": "hello", "b": None}}
    #     ddiff = DeepDiff(t1, t2)
    #     result = {'values_changed': ['root[2]: 2 ===> 4'],
    #               'type_changes': [u"root[4]['b']: 50%=<type 'str'> ===> None=<type 'NoneType'>"]}
    #     self.assertEqual(ddiff, result)

    # def test_percent_in_string(self):
    #     t1 = {"a": "hello", "b": "50%"}
    #     t2 = {"a": "hello", "b": "%s"}
    #     ddiff = DeepDiff(t1, t2)
    #     result = {'values_changed': ["root['b']: '50%' ===> '%s'"]}
    #     self.assertEqual(ddiff, result)

    # def test_curly_brackets_in_string_type_change(self):
    #     t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "{}"}}
    #     t2 = {1: 1, 2: 4, 3: 3, 4: {"a": "hello", "b": None}}
    #     ddiff = DeepDiff(t1, t2)

    #     result = {'values_changed': ['root[2]: 2 ===> 4'],
    #               'type_changes': ["root[4]['b']: {}=<type 'str'> ===> None=<type 'NoneType'>"]}

    #     self.assertEqual(ddiff, result)
