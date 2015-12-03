**DeepDiff v 0.6.0**

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
    >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3, 4]}}
    >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2]}}
    >>> ddiff = DeepDiff(t1, t2)
    >>> pprint (ddiff, indent = 2)
    {'iterable_item_removed': ["root[4]['b']: [3, 4]"]}

List difference 2:
    >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
    >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 3, 2, 3]}}
    >>> ddiff = DeepDiff(t1, t2)
    >>> pprint (ddiff, indent = 2)
    { 'iterable_item_added': ["root[4]['b']: [3]"],
      'values_changed': ["root[4]['b'][1]: 2 ===> 3", "root[4]['b'][2]: 3 ===> 2"]}

List that contains dictionary:
    >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, {1:1, 2:2}]}}
    >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, {1:3}]}}
    >>> ddiff = DeepDiff(t1, t2)
    >>> pprint (ddiff, indent = 2)
    { 'dic_item_removed': ["root[4]['b'][2][2]"],
      'values_changed': ["root[4]['b'][2][1]: 1 ===> 3"]}

Sets:
    >>> t1 = {1, 2, 8}
    >>> t2 = {1, 2, 3, 5}
    >>> ddiff = DeepDiff(t1, t2)
    >>> print (DeepDiff(t1, t2))
    {'set_item_added': ['root: [3, 5]'], 'set_item_removed': ['root: [8]']}

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

Ignoring order:
    >>> t1 = [{"a": 2}, {"b": [3, 4, {1: 1}]}]
    >>> t2 = [{"b": [3, 4, {1: 1}]}, {"a": 2}]
    ddiff = DeepDiff(t1, t2, ignore_order=True)
    >>>
    >>> print(DeepDiff(t1, t2))
    {}


**Changelog**

v0-6-0: Adding unicode support
v0-5-9: Adding decimal support
v0-5-8: Adding ignore order of unhashables support
v0-5-7: Adding ignore order support
v0-5-6: Adding slots support
v0-5-5: Adding loop detection

**Author**
Seperman

Github:  <https://github.com/seperman>
Linkedin:  <http://www.linkedin.com/in/sepehr>
ZepWorks:   <http://www.zepworks.com>
