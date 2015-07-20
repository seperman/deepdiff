#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import difflib
import datetime
from sys import version

py3 = version[0] == '3'

if py3:
    from builtins import int
    basestring = str
    numbers = (int, float, complex, datetime.datetime)
else:
    numbers = (int, float, long, complex, datetime.datetime)

from collections import Iterable

class DeepDiff(dict):

    r"""
    **DeepDiff v 0.5.2**

    Deep Difference of dictionaries, iterables, strings and almost any other object. It will recursively look for all the changes.

    **Parameters**

    t1 : A dictionary, list, string or any python object that has __dict__
        This is the first item to be compared to the second item

    t2 : dictionary, list, string or almost any python object that has __dict__
        The second item is to be compared to the first one

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
        >>> print(DeepDiff(t1, t2))
        {'type_changes': ["root[2]: 2=<type 'int'> ===> 2=<type 'str'>"]}

    Value of an item has changed
        >>> t1 = {1:1, 2:2, 3:3}
        >>> t2 = {1:1, 2:4, 3:3}
        >>> print(DeepDiff(t1, t2))
        {'values_changed': ['root[2]: 2 ===> 4']}

    Item added and/or removed
        >>> t1 = {1:1, 2:2, 3:3, 4:4}
        >>> t2 = {1:1, 2:4, 3:3, 5:5, 6:6}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (ddiff)
        {'dic_item_added': ['root[5, 6]'],
         'dic_item_removed': ['root[4]'],
         'values_changed': ['root[2]: 2 ===> 4']}

    String difference
        >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":"world"}}
        >>> t2 = {1:1, 2:4, 3:3, 4:{"a":"hello", "b":"world!"}}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (ddiff, indent = 2)
        { 'values_changed': [ 'root[2]: 2 ===> 4',
                              "root[4]['b']: 'world' ===> 'world!'"]}
        >>>
        >>> print (ddiff['values_changed'][1])
        root[4]['b']: 'world' ===> 'world!'

    String difference 2
        >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":"world!\nGoodbye!\n1\n2\nEnd"}}
        >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":"world\n1\n2\nEnd"}}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (ddiff, indent = 2)
        { 'values_changed': [ "root[4]['b']:\n"
                              '--- \n'
                              '+++ \n'
                              '@@ -1,5 +1,4 @@\n'
                              '-world!\n'
                              '-Goodbye!\n'
                              '+world\n'
                              ' 1\n'
                              ' 2\n'
                              ' End']}
        >>>
        >>> print (ddiff['values_changed'][0])
        root[4]['b']:
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
        { 'type_changes': [ "root[4]['b']: [1, 2, 3]=<type 'list'> ===> world\n"
                            '\n'
                            '\n'
                            "End=<type 'str'>"]}

    List difference
        >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
        >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2]}}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (ddiff, indent = 2)
        {'iterable_item_removed': ["root[4]['b']: [3]"]}

    List difference 2: Note that it DOES NOT take order into account
        >>> # Note that it DOES NOT take order into account
        ... t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
        >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 3, 2]}}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (ddiff, indent = 2)
        {}

    List that contains dictionary:
        >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, {1:1, 2:2}]}}
        >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, {1:3}]}}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (ddiff, indent = 2)
        { 'dic_item_removed': ["root[4]['b'][2][2]"],
          'values_changed': ["root[4]['b'][2][1]: 1 ===> 3"]}

    Named Tuples:
        >>> from collections import namedtuple
        >>> Point = namedtuple('Point', ['x', 'y'])
        >>> t1 = Point(x=11, y=22)
        >>> t2 = Point(x=11, y=23)
        >>> print (DeepDiff(t1, t2))
        {'values_changed': ['root.y: 22 ===> 23']}

    Custom objects:
        >>> class ClassA(object):
        ...     a = 1
        ...     def __init__(self, b):
        ...         self.b = b
        ...
        >>> t1 = ClassA(1)
        >>> t2 = ClassA(2)
        >>>
        >>> print(DeepDiff(t1, t2))
        {'values_changed': ['root.b: 1 ===> 2']}

    Object attribute added:
        >>> t2.c = "new attribute"
        >>> print(DeepDiff(t1, t2))
        {'attribute_added': ['root.c'], 'values_changed': ['root.b: 1 ===> 2']}

    """

    def __init__(self, t1, t2):

        self.update({"type_changes": [], "dic_item_added": [], "dic_item_removed": [],
                     "values_changed": [], "unprocessed": [], "iterable_item_added": [], "iterable_item_removed": [],
                     "attribute_added":[], "attribute_removed":[] })

        self.__diffit(t1, t2)

        if py3:
            empty_keys = [k for k, v in self.items() if not v]
        else:
            empty_keys = [k for k, v in self.iteritems() if not v]

        for k in empty_keys:
            del self[k]

    @staticmethod
    def __typestr(obj):
        '''
        python 3 returns <class 'something'> instead of <type 'something'>.
        For backward compatibility, we replace class with type.
        '''
        return str(type(obj)).replace('class', 'type')

    def __diffdict(self, t1, t2, parent, attributes_mode=False):

        if attributes_mode:
            try:
                t1 = t1.__dict__
                t2 = t2.__dict__
                item_added_key = "attribute_added"
                item_removed_key = "attribute_removed"
                parent_text = "%s.%s"
            except AttributeError:
                self['unprocessed'].append("%s: %s and %s" % (parent, t1, t2))
                return
        else:
            item_added_key = "dic_item_added"
            item_removed_key = "dic_item_removed"
            parent_text = "%s[%s]"

        t2_keys, t1_keys = [
            set(d.keys()) for d in (t2, t1)
        ]

        t_keys_intersect = t2_keys.intersection(t1_keys)

        t_keys_added = t2_keys - t_keys_intersect
        t_keys_removed = t1_keys - t_keys_intersect

        if t_keys_added:
            if attributes_mode:
                self[item_added_key].append("%s.%s" % (parent, ','.join(t_keys_added)))
            else:
                self[item_added_key].append("%s%s" % (parent, list(t_keys_added)))

        if t_keys_removed:
            if attributes_mode:
                self[item_removed_key].append("%s%s" % (parent, ','.join(t_keys_removed)))
            else:
                self[item_removed_key].append("%s%s" % (parent, list(t_keys_removed)))

        for item in t_keys_intersect:
            if not attributes_mode and isinstance(item, basestring):
                item_str = "'%s'" % item
            else:
                item_str = item
            self.__diffit(t1[item], t2[item], parent=parent_text % (parent, item_str))

    def __diff_iterable(self, t1, t2, parent="root"):
        '''
        difference of iterables except dictionaries and strings.
        '''
        try:
            if not isinstance(t1, set):
                t1_set = set(t1)
                t2_set = set(t2)
            else:
                t1_set = t1
                t2_set = t2

        # When we can't make a set since the iterable has unhashable items
        except TypeError:

            for i, (x, y) in enumerate(zip(t1, t2)):

                self.__diffit(x, y, "%s[%s]" % (parent, i))

            if len(t1) != len(t2):
                items_added = [item for item in t2 if item not in t1]
                items_removed = [item for item in t1 if item not in t2]
            else:
                items_added = None
                items_removed = None
        else:
            items_added = list(t2_set - t1_set)
            items_removed = list(t1_set - t2_set)

        if items_added:
            self["iterable_item_added"].append("%s: %s" % (parent, items_added))

        if items_removed:
            self["iterable_item_removed"].append("%s: %s" % (parent, items_removed))

    def __diffstr(self, t1, t2, parent):
        '''
        compares strings
        '''
        if '\n' in t1 or '\n' in t2:
            diff = difflib.unified_diff(t1.splitlines(), t2.splitlines(), lineterm='')
            diff = list(diff)
            if diff:
                diff = '\n'.join(diff)
                self["values_changed"].append("%s:\n%s" % (parent, diff))
        elif t1 is not t2:
            self["values_changed"].append("%s: '%s' ===> '%s'" % (parent, t1, t2))

    def __diffit(self, t1, t2, parent="root"):

        if type(t1) != type(t2):
            self["type_changes"].append("%s: %s=%s ===> %s=%s" % (parent, t1, self.__typestr(t1), t2, self.__typestr(t2)))

        elif isinstance(t1, basestring):
            self.__diffstr(t1, t2, parent)

        elif isinstance(t1, numbers):
            if t1 != t2:
                self["values_changed"].append("%s: %s ===> %s" % (parent, t1, t2))

        elif isinstance(t1, dict):
            self.__diffdict(t1, t2, parent)

        elif isinstance(t1, tuple):
            # Checking to see if it has _fields. Which probably means it is a named tuple.
            try:
                t1._fields
            # It must be a normal tuple
            except:
                self.__diff_iterable(t1, t2, parent)
            # We assume it is a namedtuple then
            else:
                self.__diffdict(t1, t2, parent, attributes_mode=True)

        elif isinstance(t1, Iterable):
            self.__diff_iterable(t1, t2, parent)

        else:
            self.__diffdict(t1, t2, parent, attributes_mode=True)

        return

    @property
    def changes(self):
        '''
        This is for backward compatibility with previous versions of DeepDiff.
        You don't need this anymore since you can access the result dictionary of changes directly from DeepDiff now:

        `DeepDiff(t1,t2) == DeepDiff(t1, t2).changes`
        '''
        return self

if __name__ == "__main__":
    import doctest
    doctest.testmod()
