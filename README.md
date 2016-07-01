# deepdiff v 1.5.0

<!-- ![Downloads](https://img.shields.io/pypi/dm/deepdiff.svg?style=flat) -->
![Python Versions](https://img.shields.io/pypi/pyversions/deepdiff.svg?style=flat)
![Doc](https://readthedocs.org/projects/deepdiff/badge/?version=latest)
![License](https://img.shields.io/pypi/l/deepdiff.svg?version=latest)
[![Build Status](https://travis-ci.org/seperman/deepdiff.svg?branch=master)](https://travis-ci.org/seperman/deepdiff)

Deep Difference of dictionaries, iterables, strings and other objects. It will recursively look for all the changes.
Tested on Python 2.7, 3.3, 3.4, 3.5, Pypy, Pypy3

## Pycon 2016

I was honored to give a talk about how DeepDiff does what it does at Pycon 2016. Please check out the video and let me know what you think:

[Diff It To Dig It Video](https://www.youtube.com/watch?v=J5r99eJIxF4)
And here is more info: <http://zepworks.com/blog/diff-it-to-digg-it/>

##Installation

###Install from PyPi:

    pip install deepdiff

### Importing

```python
>>> from deepdiff import DeepDiff
```

## Supported data types

int, string, dictionary, list, tuple, set, frozenset, OrderedDict, NamedTuple and custom objects!


## Examples

### Importing

```python
>>> from deepdiff import DeepDiff
>>> from pprint import pprint
>>> from __future__ import print_function # In case running on Python 2
```

### Same object returns empty

```python
>>> t1 = {1:1, 2:2, 3:3}
>>> t2 = t1
>>> print(DeepDiff(t1, t2))
{}
```

### Type of an item has changed

```python
>>> t1 = {1:1, 2:2, 3:3}
>>> t2 = {1:1, 2:"2", 3:3}
>>> pprint(DeepDiff(t1, t2), indent=2)
{ 'type_changes': { 'root[2]': { 'newtype': <class 'str'>,
                                 'newvalue': '2',
                                 'oldtype': <class 'int'>,
                                 'oldvalue': 2}}}
```

### Value of an item has changed

```python
>>> t1 = {1:1, 2:2, 3:3}
>>> t2 = {1:1, 2:4, 3:3}
>>> pprint(DeepDiff(t1, t2), indent=2)
{'values_changed': {'root[2]': {'newvalue': 4, 'oldvalue': 2}}}
```

### Item added and/or removed

```python
>>> t1 = {1:1, 2:2, 3:3, 4:4}
>>> t2 = {1:1, 2:4, 3:3, 5:5, 6:6}
>>> ddiff = DeepDiff(t1, t2)
>>> pprint (ddiff)
{'dic_item_added': ['root[5]', 'root[6]'],
 'dic_item_removed': ['root[4]'],
 'values_changed': {'root[2]': {'newvalue': 4, 'oldvalue': 2}}}
```

### String difference

```python
>>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":"world"}}
>>> t2 = {1:1, 2:4, 3:3, 4:{"a":"hello", "b":"world!"}}
>>> ddiff = DeepDiff(t1, t2)
>>> pprint (ddiff, indent = 2)
{ 'values_changed': { 'root[2]': {'newvalue': 4, 'oldvalue': 2},
                      "root[4]['b']": { 'newvalue': 'world!',
                                        'oldvalue': 'world'}}}
```

### String difference 2

```python
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
```

### Type change

```python
>>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
>>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":"world\n\n\nEnd"}}
>>> ddiff = DeepDiff(t1, t2)
>>> pprint (ddiff, indent = 2)
{ 'type_changes': { "root[4]['b']": { 'newtype': <class 'str'>,
                                      'newvalue': 'world\n\n\nEnd',
                                      'oldtype': <class 'list'>,
                                      'oldvalue': [1, 2, 3]}}}
```

### List difference

```python
>>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3, 4]}}
>>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2]}}
>>> ddiff = DeepDiff(t1, t2)
>>> pprint (ddiff, indent = 2)
{'iterable_item_removed': {"root[4]['b'][2]": 3, "root[4]['b'][3]": 4}}
```

### List difference 2:

```python
>>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
>>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 3, 2, 3]}}
>>> ddiff = DeepDiff(t1, t2)
>>> pprint (ddiff, indent = 2)
{ 'iterable_item_added': {"root[4]['b'][3]": 3},
  'values_changed': { "root[4]['b'][1]": {'newvalue': 3, 'oldvalue': 2},
                      "root[4]['b'][2]": {'newvalue': 2, 'oldvalue': 3}}}
```

### List difference ignoring order or duplicates: (with the same dictionaries as above)

```python
>>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
>>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 3, 2, 3]}}
>>> ddiff = DeepDiff(t1, t2, ignore_order=True)
>>> print (ddiff)
{}
```

### List difference ignoring order or duplicates for objects that have hash collision (Advanced)

It might rarely happen that Python objects have hash collision using the built-in hash function:

```python
>>> a='\0B'
>>> hash(a)
64
>>> b='\0\0C'
>>> hash(b)
64
```

Although `ignore_order` flag uses hash of items to calculate what is added or removed, we still get the right answer.

```python
>>> list1=[a,b]
>>> list2=[a,a]
>>> DeepDiff(list1,list2, ignore_order=True)
{'set_item_removed': set(["root['\x00\x00C']"])}
```

### List that contains dictionary:

```python
>>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, {1:1, 2:2}]}}
>>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, {1:3}]}}
>>> ddiff = DeepDiff(t1, t2)
>>> pprint (ddiff, indent = 2)
{ 'dic_item_removed': ["root[4]['b'][2][2]"],
  'values_changed': {"root[4]['b'][2][1]": {'newvalue': 3, 'oldvalue': 1}}}
```

### Sets:

```python
>>> t1 = {1, 2, 8}
>>> t2 = {1, 2, 3, 5}
>>> ddiff = DeepDiff(t1, t2)
>>> pprint (DeepDiff(t1, t2))
{'set_item_added': ['root[3]', 'root[5]'], 'set_item_removed': ['root[8]']}
```

### Named Tuples:

```python
>>> from collections import namedtuple
>>> Point = namedtuple('Point', ['x', 'y'])
>>> t1 = Point(x=11, y=22)
>>> t2 = Point(x=11, y=23)
>>> pprint (DeepDiff(t1, t2))
{'values_changed': {'root.y': {'newvalue': 23, 'oldvalue': 22}}}
```

### Custom objects:

```python
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
```

### Object attribute added:

```python
>>> t2.c = "new attribute"
>>> pprint(DeepDiff(t1, t2))
{'attribute_added': ['root.c'],
 'values_changed': {'root.b': {'newvalue': 2, 'oldvalue': 1}}}
```

## Difference with Json Patch

Unlike [Json Patch](https://tools.ietf.org/html/rfc6902) which is designed only for Json objects, DeepDiff is designed specifically for almost all Python types. In addition to that, DeepDiff checks for type changes and attribute value changes that Json Patch does not cover since there are no such things in Json. Last but not least, DeepDiff gives you the exact path of the item(s) that were changed in Python syntax.

Example in Json Patch for replacing:

`{ "op": "replace", "path": "/a/b/c", "value": 42 }`

Example in DeepDiff for the same operation:

```python
>>> item1 = {'a':{'b':{'c':'foo'}}}
>>> item2 = {'a':{'b':{'c':42}}}
>>> DeepDiff(item1, item2)
{'type_changes': {"root['a']['b']['c']": {'oldtype': <type 'str'>, 'newvalue': 42, 'oldvalue': 'foo', 'newtype': <type 'int'>}}}
```


##Documentation

<http://deepdiff.readthedocs.org/en/latest/>

##Changelog

- v1-5-0: Fixing ignore order containers with unordered items. Adding significant digits when comparing decimals. Changes property is deprecated.
- v1-1-0: Changing Set, Dictionary and Object Attribute Add/Removal to be reported as Set instead of List. Adding Pypy compatibility.
- v1-0-2: Checking for ImmutableMapping type instead of dict
- v1-0-1: Better ignore order support
- v1-0-0: Restructuring output to make it more useful. This is NOT backward compatible.
- v0-6-1: Fixiing iterables with unhashable when order is ignored
- v0-6-0: Adding unicode support
- v0-5-9: Adding decimal support
- v0-5-8: Adding ignore order of unhashables support
- v0-5-7: Adding ignore order support
- v0-5-6: Adding slots support
- v0-5-5: Adding loop detection

##Author

Seperman (Sep Dehpour)

- Github:  <https://github.com/seperman>
- Linkedin:  <http://www.linkedin.com/in/sepehr>
- ZepWorks:   <http://www.zepworks.com>

Thanks to:

- nfvs for Travis-CI setup script
- brbsix for initial Py3 porting
- WangFenjin for unicode support
- timoilya for comparing list of sets when ignoring order
- Bernhard10 for significant digits comparison
