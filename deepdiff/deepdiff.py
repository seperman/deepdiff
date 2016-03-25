#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import difflib
import datetime
try:
    import cPickle as pickle
except:
    import pickle
from decimal import Decimal
from sys import version
from collections import Iterable
from collections import namedtuple
from collections import MutableMapping

py_major_version = version[0]
py_minor_version = version[2]

py3 = py_major_version == '3'

if (py_major_version, py_minor_version) == (2.6):
    from sys import exit
    exit('Python 2.6 is not supported.')

if py3:
    from builtins import int
    strings = (str, bytes)  # which are both basestring
    numbers = (int, float, complex, datetime.datetime, Decimal)
    from itertools import zip_longest
    # from _string import formatter_field_name_split
    items = 'items'
else:
    strings = (str, unicode)
    numbers = (int, float, long, complex, datetime.datetime, Decimal)
    from itertools import izip_longest as zip_longest
    items = 'iteritems'
    # formatter_field_name_split = str._formatter_field_name_split

IndexedHash = namedtuple('IndexedHash', 'index item')


class ListItemRemovedOrAdded(object):

    '''Class of conditions to be checked'''

    pass

INDEX_VS_ATTRIBUTE = ('[%s]', '.%s')


class DeepDiff(dict):

    r"""
    **DeepDiff v 1.0.2**

    Deep Difference of dictionaries, iterables, strings and almost any other object.
    It will recursively look for all the changes.

    **Parameters**

    t1 : A dictionary, list, string or any python object that has __dict__ or __slots__
        This is the first item to be compared to the second item

    t2 : dictionary, list, string or almost any python object that has __dict__ or __slots__
        The second item is to be compared to the first one

    ignore_order : Boolean, defalt=False ignores orders for iterables.
        Note that if you have iterables contatining any unhashable, ignoring order can be expensive.
        Ignoring order for an iterable containing any unhashable
        will include duplicates if there are any in the iterable.
        Ignoring order for an iterable containing only hashables
        will not include duplicates in the iterable.

    **Returns**

        A DeepDiff object that has already calculated the difference of the 2 items.

    **Supported data types**

    int, string, unicode, dictionary, list, tuple, set, frozenset, OrderedDict, NamedTuple and custom objects!

    **Examples**

    Importing
        >>> from deepdiff import DeepDiff
        >>> from pprint import pprint
        >>> from __future__ import print_function # In case running on Python 2

    Same object returns empty
        >>> t1 = {1:1, 2:2, 3:3}
        >>> t2 = t1
        >>> print(DeepDiff(t1, t2))
        {}

    Type of an item has changed
        >>> t1 = {1:1, 2:2, 3:3}
        >>> t2 = {1:1, 2:"2", 3:3}
        >>> pprint(DeepDiff(t1, t2), indent=2)
        { 'type_changes': { 'root[2]': { 'newtype': <class 'str'>,
                                         'newvalue': '2',
                                         'oldtype': <class 'int'>,
                                         'oldvalue': 2}}}

    Value of an item has changed
        >>> t1 = {1:1, 2:2, 3:3}
        >>> t2 = {1:1, 2:4, 3:3}
        >>> pprint(DeepDiff(t1, t2), indent=2)
        {'values_changed': {'root[2]': {'newvalue': 4, 'oldvalue': 2}}}

    Item added and/or removed
        >>> t1 = {1:1, 2:2, 3:3, 4:4}
        >>> t2 = {1:1, 2:4, 3:3, 5:5, 6:6}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (ddiff)
        {'dic_item_added': ['root[5]', 'root[6]'],
         'dic_item_removed': ['root[4]'],
         'values_changed': {'root[2]': {'newvalue': 4, 'oldvalue': 2}}}

    String difference
        >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":"world"}}
        >>> t2 = {1:1, 2:4, 3:3, 4:{"a":"hello", "b":"world!"}}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (ddiff, indent = 2)
        { 'values_changed': { 'root[2]': {'newvalue': 4, 'oldvalue': 2},
                              "root[4]['b']": { 'newvalue': 'world!',
                                                'oldvalue': 'world'}}}


    String difference 2
        >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":"world!\nGoodbye!\n1\n2\nEnd"}}
        >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":"world\n1\n2\nEnd"}}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (ddiff, indent = 2)
        { 'values_changed': { "root[4]['b']": { 'diff': '--- \n'
                                                        '+++ \n'
                                                        '@@ -1,5 +1,4 @@\n'
                                                        '-world!\n'
                                                        '-Goodbye!\n'
                                                        '+world\n'
                                                        ' 1\n'
                                                        ' 2\n'
                                                        ' End',
                                                'newvalue': 'world\n1\n2\nEnd',
                                                'oldvalue': 'world!\n'
                                                            'Goodbye!\n'
                                                            '1\n'
                                                            '2\n'
                                                            'End'}}}

        >>> 
        >>> print (ddiff['values_changed']["root[4]['b']"]["diff"])
        --- 
        +++ 
        @@ -1,5 +1,4 @@
        -world!
        -Goodbye!
        +world
         1
         2
         End

    Type change
        >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
        >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":"world\n\n\nEnd"}}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (ddiff, indent = 2)
        { 'type_changes': { "root[4]['b']": { 'newtype': <class 'str'>,
                                              'newvalue': 'world\n\n\nEnd',
                                              'oldtype': <class 'list'>,
                                              'oldvalue': [1, 2, 3]}}}

    List difference
        >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3, 4]}}
        >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2]}}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (ddiff, indent = 2)
        {'iterable_item_removed': {"root[4]['b'][2]": 3, "root[4]['b'][3]": 4}}

    List difference 2:
        >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
        >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 3, 2, 3]}}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (ddiff, indent = 2)
        { 'iterable_item_added': {"root[4]['b'][3]": 3},
          'values_changed': { "root[4]['b'][1]": {'newvalue': 3, 'oldvalue': 2},
                              "root[4]['b'][2]": {'newvalue': 2, 'oldvalue': 3}}}

    List difference ignoring order or duplicates: (with the same dictionaries as above)
        >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
        >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 3, 2, 3]}}
        >>> ddiff = DeepDiff(t1, t2, ignore_order=True)
        >>> print (ddiff)
        {}

    List that contains dictionary:
        >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, {1:1, 2:2}]}}
        >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, {1:3}]}}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (ddiff, indent = 2)
        { 'dic_item_removed': ["root[4]['b'][2][2]"],
          'values_changed': {"root[4]['b'][2][1]": {'newvalue': 3, 'oldvalue': 1}}}

    Sets:
        >>> t1 = {1, 2, 8}
        >>> t2 = {1, 2, 3, 5}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (DeepDiff(t1, t2))
        {'set_item_added': ['root[3]', 'root[5]'], 'set_item_removed': ['root[8]']}

    Named Tuples:
        >>> from collections import namedtuple
        >>> Point = namedtuple('Point', ['x', 'y'])
        >>> t1 = Point(x=11, y=22)
        >>> t2 = Point(x=11, y=23)
        >>> pprint (DeepDiff(t1, t2))
        {'values_changed': {'root.y': {'newvalue': 23, 'oldvalue': 22}}}

    Custom objects:
        >>> class ClassA(object):
        ...     a = 1
        ...     def __init__(self, b):
        ...         self.b = b
        ... 
        >>> t1 = ClassA(1)
        >>> t2 = ClassA(2)
        >>> 
        >>> pprint(DeepDiff(t1, t2))
        {'values_changed': {'root.b': {'newvalue': 2, 'oldvalue': 1}}}

    Object attribute added:
        >>> t2.c = "new attribute"
        >>> pprint(DeepDiff(t1, t2))
        {'attribute_added': ['root.c'],
         'values_changed': {'root.b': {'newvalue': 2, 'oldvalue': 1}}}
    """

    def __init__(self, t1, t2, ignore_order=False):
        self.ignore_order = ignore_order

        self.update({"type_changes": {}, "dic_item_added": [], "dic_item_removed": [],
                     "values_changed": {}, "unprocessed": [], "iterable_item_added": {}, "iterable_item_removed": {},
                     "attribute_added": [], "attribute_removed": [], "set_item_removed": [], "set_item_added": []})

        self.__diff(t1, t2, parents_ids=frozenset({id(t1)}))

        empty_keys = [k for k, v in getattr(self, items)() if not v]

        for k in empty_keys:
            del self[k]

    @staticmethod
    def __extend_result_list(keys, parent, result_obj, print_as_attribute=False):
        key_text = "%s{}".format(INDEX_VS_ATTRIBUTE[print_as_attribute])
        formatted_items = []
        for i in keys:
            i = "'%s'" % i if not print_as_attribute and isinstance(i, strings) else i
            formatted_items.append(key_text % (parent, i))
        result_obj.extend(formatted_items)

    def __diff_obj(self, t1, t2, parent, parents_ids=frozenset({})):
        '''Difference of 2 objects'''
        try:
            t1 = t1.__dict__
            t2 = t2.__dict__
        except AttributeError:
            try:
                t1 = {i: getattr(t1, i) for i in t1.__slots__}
                t2 = {i: getattr(t2, i) for i in t2.__slots__}
            except AttributeError:
                self['unprocessed'].append("%s: %s and %s" % (parent, t1, t2))
                return

        self.__diff_dict(t1, t2, parent, parents_ids, print_as_attribute=True)

    def __diff_dict(self, t1, t2, parent, parents_ids=frozenset({}), print_as_attribute=False):
        '''Difference of 2 dictionaries'''
        if print_as_attribute:
            item_added_key = "attribute_added"
            item_removed_key = "attribute_removed"
            parent_text = "%s.%s"
        else:
            item_added_key = "dic_item_added"
            item_removed_key = "dic_item_removed"
            parent_text = "%s[%s]"

        t1_keys = set(t1.keys())
        t2_keys = set(t2.keys())

        t_keys_intersect = t2_keys.intersection(t1_keys)

        t_keys_added = t2_keys - t_keys_intersect
        t_keys_removed = t1_keys - t_keys_intersect

        if t_keys_added:
            self.__extend_result_list(keys=t_keys_added, parent=parent,
                                      result_obj=self[item_added_key], print_as_attribute=print_as_attribute)

        if t_keys_removed:
            self.__extend_result_list(keys=t_keys_removed, parent=parent,
                                      result_obj=self[item_removed_key], print_as_attribute=print_as_attribute)

        self.__diff_common_children(
            t1, t2, t_keys_intersect, print_as_attribute, parents_ids, parent, parent_text)

    def __diff_common_children(self, t1, t2, t_keys_intersect, print_as_attribute, parents_ids, parent, parent_text):
        '''Difference between common attributes of objects or values of common keys of dictionaries'''
        for item_key in t_keys_intersect:
            if not print_as_attribute and isinstance(item_key, strings):
                item_key_str = "'%s'" % item_key
            else:
                item_key_str = item_key

            t1_child = t1[item_key]
            t2_child = t2[item_key]

            item_id = id(t1_child)

            if parents_ids and item_id in parents_ids:
                # print ("Warning, a loop is detected in {}.\n".format(parent_text % (parent, item_key_str)))
                continue

            parents_added = set(parents_ids)
            parents_added.add(item_id)
            parents_added = frozenset(parents_added)

            self.__diff(t1_child, t2_child, parent=parent_text %
                        (parent, item_key_str), parents_ids=parents_added)

    def __diff_set(self, t1, t2, parent="root"):
        '''Difference of sets'''
        items_added = list(t2 - t1)
        items_removed = list(t1 - t2)

        if items_removed:
            self.__extend_result_list(
                keys=items_removed, parent=parent, result_obj=self["set_item_removed"])

        if items_added:
            self.__extend_result_list(
                keys=items_added, parent=parent, result_obj=self["set_item_added"])

    def __diff_iterable(self, t1, t2, parent="root", parents_ids=frozenset({})):
        '''Difference of iterables except dictionaries, sets and strings.'''
        items_removed = {}
        items_added = {}

        for i, (x, y) in enumerate(zip_longest(t1, t2, fillvalue=ListItemRemovedOrAdded)):

            if y is ListItemRemovedOrAdded:
                items_removed["%s[%s]" % (parent, i)] = x
            elif x is ListItemRemovedOrAdded:
                items_added["%s[%s]" % (parent, i)] = y
            else:
                self.__diff(x, y, "%s[%s]" % (parent, i), parents_ids)

        self["iterable_item_removed"].update(items_removed)
        self["iterable_item_added"].update(items_added)

    def __diff_str(self, t1, t2, parent):
        '''Compare strings'''
        if '\n' in t1 or '\n' in t2:
            diff = difflib.unified_diff(
                t1.splitlines(), t2.splitlines(), lineterm='')
            diff = list(diff)
            if diff:
                diff = '\n'.join(diff)
                self["values_changed"][parent] = {
                    "oldvalue": t1, "newvalue": t2, "diff": diff}
        elif t1 != t2:
            self["values_changed"][parent] = {"oldvalue": t1, "newvalue": t2}

    def __diff_tuple(self, t1, t2, parent, parents_ids):
        # Checking to see if it has _fields. Which probably means it is a named
        # tuple.
        try:
            t1._fields
        # It must be a normal tuple
        except:
            self.__diff_iterable(t1, t2, parent, parents_ids)
        # We assume it is a namedtuple then
        else:
            self.__diff_obj(t1, t2, parent, parents_ids)

    @staticmethod
    def __create_hashtable(t, parent):
        '''Create hashtable of {item_hash: item}'''
        hashes = {}
        for (i, item) in enumerate(t):
            try:
                item_hash = hash(item)
            except TypeError:
                try:
                    item_hash = hash(pickle.dumps(item))
                except Exception as e:
                    print ("Warning: Can not produce a hash for %s item in %s and\
                        thus not counting this object. %s" % (item, parent, e))
                else:
                    hashes[item_hash] = IndexedHash(i, item)
            else:
                hashes[item_hash] = IndexedHash(i, item)
        return hashes

    def __diff_unhashable_iterable(self, t1, t2, parent):
        '''Diff of unhashable iterables. Only used when ignoring the order.'''
        t1_hashtable = self.__create_hashtable(t1, parent)
        t2_hashtable = self.__create_hashtable(t2, parent)

        t1_hashes = set(t1_hashtable.keys())
        t2_hashes = set(t2_hashtable.keys())

        hashes_added = t2_hashes - t1_hashes
        hashes_removed = t1_hashes - t2_hashes

        items_added = {"%s[%s]" % (parent, t2_hashtable[hash_value].index): t2_hashtable[
            hash_value].item for hash_value in hashes_added}

        items_removed = {"%s[%s]" % (parent, t1_hashtable[hash_value].index): t1_hashtable[
            hash_value].item for hash_value in hashes_removed}

        self["iterable_item_removed"].update(items_removed)
        self["iterable_item_added"].update(items_added)

    def __diff(self, t1, t2, parent="root", parents_ids=frozenset({})):
        '''The main diff method'''
        if t1 is t2:
            return

        if type(t1) != type(t2):
            self["type_changes"][parent] = {
                "oldvalue": t1, "newvalue": t2, "oldtype": type(t1), "newtype": type(t2)}

        elif isinstance(t1, strings):
            self.__diff_str(t1, t2, parent)

        elif isinstance(t1, numbers):
            if t1 != t2:
                self["values_changed"][parent] = {
                    "oldvalue": t1, "newvalue": t2}

        elif isinstance(t1, MutableMapping):
            self.__diff_dict(t1, t2, parent, parents_ids)

        elif isinstance(t1, tuple):
            self.__diff_tuple(t1, t2, parent, parents_ids)

        elif isinstance(t1, (set, frozenset)):
            self.__diff_set(t1, t2, parent=parent)

        elif isinstance(t1, Iterable):
            if self.ignore_order:
                try:
                    t1 = set(t1)
                    t2 = set(t2)
                # When we can't make a set since the iterable has unhashable
                # items
                except TypeError:
                    self.__diff_unhashable_iterable(t1, t2, parent)
                else:
                    self.__diff_set(t1, t2, parent=parent)
            else:
                self.__diff_iterable(t1, t2, parent, parents_ids)

        else:
            self.__diff_obj(t1, t2, parent, parents_ids)

        return

    @property
    def changes(self):
        '''
        For backward compatibility with previous versions of DeepDiff.

        You don't need this anymore since you can access the result dictionary of changes directly from DeepDiff now:
        DeepDiff(t1,t2) == DeepDiff(t1, t2).changes
        '''
        return self


if __name__ == "__main__":
    import doctest
    doctest.testmod()
