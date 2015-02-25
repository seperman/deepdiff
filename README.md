deepdiff v 0.2
========

Deep Difference of dictionaries, iterables, strings and other objects. It will recursively look for all the changes.


##Installation

Install from PyPi:

    pip install deepdiff

If you are Python3 you need to also install:

    pip install future six

##Example usage

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


##Documents

http://deepdiff.readthedocs.org/en/latest/



##Author

Seperman
Github:  https://github.com/seperman
Linkedin:  http://www.linkedin.com/in/sepehr
ZepWorks:   http://www.zepworks.com

Thanks to:
brbsix for Py3 porting
