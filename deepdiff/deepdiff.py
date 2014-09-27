#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import difflib
import datetime
from collections import Iterable

class DeepDiff(object):
    r"""
    Deep Difference of dictionaries, iterables, strings and other objects. It will recursively look for all the changes.

    Parameters
    ----------
    t1 : A dictionary, list, string or any python object that has __dict__
        This is the first item to be compared to the second item
    
    t2 : dictionary, list, string or almost any python object that has __dict__
        The second item to be compared to the first one

    Returns
    -------
        A DeepDiff object that has already calculated the difference of the 2 items. You can access the result in the 'changes' attribute


    Examples
    --------


        >>> from deepdiff import DeepDiff
        >>> from pprint import pprint
        >>> from __future__ import print_function


    Same object returns empty
        >>> t1 = {1:1, 2:2, 3:3}
        >>> t2 = t1
        >>> ddiff = DeepDiff(t1, t2)
        >>> print (ddiff.changes)
        {}


    Type of an item has changed
        >>> t1 = {1:1, 2:2, 3:3}
        >>> t2 = {1:1, 2:"2", 3:3}
        >>> ddiff = DeepDiff(t1, t2)
        >>> print (ddiff.changes)
        {'type_changes': ["root[2]: 2=<type 'int'> vs. 2=<type 'str'>"]}


    Value of an item has changed
        >>> t1 = {1:1, 2:2, 3:3}
        >>> t2 = {1:1, 2:4, 3:3}
        >>> ddiff = DeepDiff(t1, t2)
        >>> print (ddiff.changes)
        {'values_changed': ['root[2]: 2 ====>> 4']}


    Item added and/or removed
        >>> t1 = {1:1, 2:2, 3:3, 4:4}
        >>> t2 = {1:1, 2:4, 3:3, 5:5, 6:6}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (ddiff.changes)
        {'dic_item_added': ['root[5, 6]'],
         'dic_item_removed': ['root[4]'],
         'values_changed': ['root[2]: 2 ====>> 4']}


    String difference
        >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":"world"}}
        >>> t2 = {1:1, 2:4, 3:3, 4:{"a":"hello", "b":"world!"}}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (ddiff.changes, indent = 2)
        { 'values_changed': [ 'root[2]: 2 ====>> 4',
                              "root[4]['b']:\n--- \n+++ \n@@ -1 +1 @@\n-world\n+world!"]}
        >>>
        >>> print (ddiff.changes['values_changed'][1])
        root[4]['b']:
        --- 
        +++ 
        @@ -1 +1 @@
        -world
        +world!


    String difference 2        
        >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":"world!\nGoodbye!\n1\n2\nEnd"}}
        >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":"world\n1\n2\nEnd"}}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (ddiff.changes, indent = 2)
        { 'values_changed': [ "root[4]['b']:\n--- \n+++ \n@@ -1,5 +1,4 @@\n-world!\n-Goodbye!\n+world\n 1\n 2\n End"]}
        >>>
        >>> print (ddiff.changes['values_changed'][0])
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
        >>> pprint (ddiff.changes, indent = 2)
        { 'type_changes': [ "root[4]['b']: [1, 2, 3]=<type 'list'> vs. world\n\n\nEnd=<type 'str'>"]}

    List difference
        >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
        >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2]}}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (ddiff.changes, indent = 2)
        { 'list_removed': ["root[4]['b']: [3]"]}

    List difference 2: Note that it DOES NOT take order into account
        >>> # Note that it DOES NOT take order into account
        ... t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
        >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 3, 2]}}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (ddiff.changes, indent = 2)
        { }


    List that contains dictionary:
        >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, {1:1, 2:2}]}}
        >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, {1:3}]}}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (ddiff.changes, indent = 2)
        { 'dic_item_removed': ["root[4]['b'][2][2]"],
          'values_changed': ["root[4]['b'][2][1]: 1 ====>> 3"]}

    """

    def __init__(self, t1, t2):

        self.changes = {"type_changes":[], "dic_item_added":[], "dic_item_removed":[], "values_changed":[], "unprocessed":[], "list_added":[], "list_removed":[]}
        
        self.diffit(t1, t2)

        self.changes = dict((k, v) for k, v in self.changes.iteritems() if v)


    # @property
    # def result(self):
    #     return dumps(self.changes, indent=2)

    def diffdict(self, t1, t2, parent):


        t2_keys, t1_keys = [
            set(d.keys()) for d in (t2, t1)
        ]
    
        t_keys_intersect = t2_keys.intersection(t1_keys)

        t_keys_added = t2_keys - t_keys_intersect
        t_keys_removed = t1_keys - t_keys_intersect

        if t_keys_added:
            self.changes["dic_item_added"].append("%s%s" % (parent, list(t_keys_added)))

        if t_keys_removed:
            self.changes["dic_item_removed"].append("%s%s" % (parent, list(t_keys_removed)))

        for item in t_keys_intersect:
            if isinstance(item, basestring):
                item_str = "'%s'" % item
            else:
                item_str = item
            self.diffit(t1[item], t2[item], parent="%s[%s]" % (parent, item_str))



    def diffit(self, t1, t2, parent="root"):

        if type(t1) != type(t2):
            self.changes["type_changes"].append("%s: %s=%s vs. %s=%s" % (parent, t1, type(t1), t2, type(t2)))

        elif isinstance(t1, basestring):
            diff = difflib.unified_diff(t1.splitlines(), t2.splitlines(), lineterm='')
            diff = list(diff)
            if diff:
                diff = '\n'.join(diff)
                self.changes["values_changed"].append("%s:\n%s" % (parent, diff))

        elif isinstance(t1, (int, long, float, complex, datetime.datetime)):
            if t1 != t2:
                self.changes["values_changed"].append("%s: %s ====>> %s" % (parent, t1, t2))
            
        
        elif isinstance(t1, dict):
            self.diffdict(t1, t2, parent)

        elif isinstance(t1, Iterable):

            try:
                t1_set = set(t1)
                t2_set = set(t2)
            # When we can't make a set since the iterable has unhashable items
            except TypeError:

                for i, (x, y) in  enumerate(zip(t1, t2)):

                    self.diffit(x, y, "%s[%s]" % (parent, i))

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
                self.changes["list_added"].append( "%s: %s" % (parent, items_added) )

            if items_removed:
                self.changes["list_removed"].append( "%s: %s" % (parent, items_removed) )

        else:
            try:
                t1_dict = t1.__dict__
                t2_dict = t2.__dict__
            except AttributeError:
                pass
            else:
                self.diffdict(t1_dict, t2_dict, parent)

        return




if __name__ == "__main__":
    import doctest
    doctest.testmod()
