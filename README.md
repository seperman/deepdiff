# deepdiff v 2.5.1

<!-- ![Downloads](https://img.shields.io/pypi/dm/deepdiff.svg?style=flat) -->
![Python Versions](https://img.shields.io/pypi/pyversions/deepdiff.svg?style=flat)
![Doc](https://readthedocs.org/projects/deepdiff/badge/?version=latest)
![License](https://img.shields.io/pypi/l/deepdiff.svg?version=latest)
[![Build Status](https://travis-ci.org/seperman/deepdiff.svg?branch=master)](https://travis-ci.org/seperman/deepdiff)
[![Coverage Status](https://coveralls.io/repos/github/seperman/deepdiff/badge.svg?branch=master)](https://coveralls.io/github/seperman/deepdiff?branch=master)

Deep Difference of dictionaries, iterables, strings and other objects. It will recursively look for all the changes.
Tested on Python 2.7, 3.3, 3.4, 3.5, Pypy, Pypy3

## Table of Contents

- [Installation](#Installation)
- [Parameters](#parameters)
- [Ignore Order](#ignore-order)
- [Report repetitions](#report-repetitions)
- [Exclude types or paths](#exclude-type-or-paths)
- [Significant Digits](#significant-digits)
- [Verbose Level](#verbose-level)
- [Deep Search](#deep-search)
- [Using DeepDiff in unit tests](#using-deepdiff-in-unit-tests)
- [Difference with Json Patch](#difference-with-json-patch)
- [Examples](#examples)
- [Documentation](http://deepdiff.readthedocs.io/en/latest/)


##Installation

###Install from PyPi:

    pip install deepdiff

### Importing

```python
>>> from deepdiff import DeepDiff  # For Deep Difference of 2 objects
>>> from deepdiff import DeepSearch  # For finding if item exists in an object
```

## Parameters

In addition to the 2 objects being compared:

- [ignore_order](#ignore-order)
- [report_repetition](#report-repetitions)
- [verbose_level](#verbose-level)

## Supported data types

int, string, dictionary, list, tuple, set, frozenset, OrderedDict, NamedTuple and custom objects!

## Ignore Order

Sometimes you don't care about the order of objects when comparing them. In those cases, you can set `ignore_order=True`. However this flag won't report the repetitions to you. You need to additionally enable `report_report_repetition=True` for getting a report of repetitions.

### List difference ignoring order or duplicates

```python
>>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
>>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 3, 2, 3]}}
>>> ddiff = DeepDiff(t1, t2, ignore_order=True)
>>> print (ddiff)
{}
```

## Report repetitions

This flag ONLY works when ignoring order is enabled.
Note that this feature is experimental.

```python
t1 = [1, 3, 1, 4]
t2 = [4, 4, 1]
ddiff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True)
print(ddiff)
```

which will print you:

```python
{'iterable_item_removed': {'root[1]': 3},
  'repetition_change': {'root[0]': {'old_repeat': 2,
                                    'old_indexes': [0, 2],
                                    'new_indexes': [2],
                                    'value': 1,
                                    'new_repeat': 1},
                        'root[3]': {'old_repeat': 1,
                                    'old_indexes': [3],
                                    'new_indexes': [0, 1],
                                    'value': 4,
                                    'new_repeat': 2}}}
```

## Exclude types or paths

### Exclude certain types from comparison:
```python
>>> l1 = logging.getLogger("test")
>>> l2 = logging.getLogger("test2")
>>> t1 = {"log": l1, 2: 1337}
>>> t2 = {"log": l2, 2: 1337}
>>> print(DeepDiff(t1, t2, exclude_types={logging.Logger}))
{}
```

### Exclude part of your object tree from comparison:
```python
>>> t1 = {"for life": "vegan", "ingredients": ["no meat", "no eggs", "no dairy"]}
>>> t2 = {"for life": "vegan", "ingredients": ["veggies", "tofu", "soy sauce"]}
>>> print (DeepDiff(t1, t2, exclude_paths={"root['ingredients']"}))
{}
```

## Significant Digits

Digits **after** the decimal point. Internally it uses "{:.Xf}".format(Your Number) to compare numbers where X=significant_digits

```python
>>> t1 = Decimal('1.52')
>>> t2 = Decimal('1.57')
>>> DeepDiff(t1, t2, significant_digits=0)
{}
>>> DeepDiff(t1, t2, significant_digits=1)
{'values_changed': {'root': {'old_value': Decimal('1.52'), 'new_value': Decimal('1.57')}}}
```

Approximate float comparison:

```python
>>> t1 = [ 1.1129, 1.3359 ]
>>> t2 = [ 1.113, 1.3362 ]
>>> pprint(DeepDiff(t1, t2, significant_digits=3))
{}
>>> pprint(DeepDiff(t1, t2))
{'values_changed': {'root[0]': {'new_value': 1.113, 'old_value': 1.1129},
                    'root[1]': {'new_value': 1.3362, 'old_value': 1.3359}}}
>>> pprint(DeepDiff(1.23*10**20, 1.24*10**20, significant_digits=1))
{'values_changed': {'root': {'new_value': 1.24e+20, 'old_value': 1.23e+20}}}
```

## Verbose Level

Verbose level by default is 1. The possible values are 0, 1 and 2.

- Verbose level 0: won't report values when type changed. [Example](##type-of-an-item-has-changed)
- Verbose level 1: default
- Verbose level 2: will report values when custom objects or dictionaries have items added or removed. [Example](#items-added-or-removed-verbose)

## Deep Search
(New in v2-1-0)

DeepDiff comes with a utility to find the path to the item you are looking for.
It is called DeepSearch and it has a similar interface to DeepDiff.

Let's say you have a huge nested object and want to see if any item with the word `somewhere` exists in it.

```py
from deepdiff import DeepSearch
obj = {"long": "somewhere", "string": 2, 0: 0, "somewhere": "around"}
ds = DeepSearch(obj, item, verbose_level=2)
print(ds)
```

Which will print:

```py
{'matched_paths': {"root['somewhere']": "around"},
 'matched_values': {"root['long']": "somewhere"}}
```

Tip: An interesting use case is to search inside `locals()` when doing pdb.

## Using DeepDiff in unit tests

`result` is the output of the function that is being tests.
`expected` is the expected output of the function.

```python
assertEqual(DeepDiff(result, expected), {})
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
{'type_changes': {"root['a']['b']['c']": {'old_type': <type 'str'>, 'new_value': 42, 'old_value': 'foo', 'new_type': <type 'int'>}}}
```

# Examples

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
{ 'type_changes': { 'root[2]': { 'new_type': <class 'str'>,
                                 'new_value': '2',
                                 'old_type': <class 'int'>,
                                 'old_value': 2}}}
```

And if you don't care about the value of items that have changed type, please set verbose level to 0:

```python
>>> t1 = {1:1, 2:2, 3:3}
>>> t2 = {1:1, 2:"2", 3:3}
>>> pprint(DeepDiff(t1, t2, verbose_level=0), indent=2)
{ 'type_changes': { 'root[2]': { 'new_type': <class 'str'>,
                                 'old_type': <class 'int'>,}}}
```


### Value of an item has changed

```python
>>> t1 = {1:1, 2:2, 3:3}
>>> t2 = {1:1, 2:4, 3:3}
>>> pprint(DeepDiff(t1, t2), indent=2)
{'values_changed': {'root[2]': {'new_value': 4, 'old_value': 2}}}
```

### Item added or removed

```python
>>> t1 = {1:1, 3:3, 4:4}
>>> t2 = {1:1, 3:3, 5:5, 6:6}
>>> ddiff = DeepDiff(t1, t2)
>>> pprint(ddiff)
{'dictionary_item_added': {'root[5]', 'root[6]'},
 'dictionary_item_removed': {'root[4]'}}
```

#### Items added or removed verbose

And if you would like to know the values of items added or removed, please set the verbose_level to 2:

```python
>>> t1 = {1:1, 3:3, 4:4}
>>> t2 = {1:1, 3:3, 5:5, 6:6}
>>> ddiff = DeepDiff(t1, t2, verbose_level=2)
>>> pprint(ddiff, indent=2)
{ 'dictionary_item_added': {'root[5]': 5, 'root[6]': 6},
  'dictionary_item_removed': {'root[4]': 4}}
```

### String difference

```python
>>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":"world"}}
>>> t2 = {1:1, 2:4, 3:3, 4:{"a":"hello", "b":"world!"}}
>>> ddiff = DeepDiff(t1, t2)
>>> pprint (ddiff, indent = 2)
{ 'values_changed': { 'root[2]': {'new_value': 4, 'old_value': 2},
                      "root[4]['b']": { 'new_value': 'world!',
                                        'old_value': 'world'}}}
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
                                        'new_value': 'world\n1\n2\nEnd',
                                        'old_value': 'world!\n'
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

### List difference

```python
>>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3, 4]}}
>>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2]}}
>>> ddiff = DeepDiff(t1, t2)
>>> pprint (ddiff, indent = 2)
{'iterable_item_removed': {"root[4]['b'][2]": 3, "root[4]['b'][3]": 4}}
```

### List difference Example 2

```python
>>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
>>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 3, 2, 3]}}
>>> ddiff = DeepDiff(t1, t2)
>>> pprint (ddiff, indent = 2)
{ 'iterable_item_added': {"root[4]['b'][3]": 3},
  'values_changed': { "root[4]['b'][1]": {'new_value': 3, 'old_value': 2},
                      "root[4]['b'][2]": {'new_value': 2, 'old_value': 3}}}
```

### List that contains dictionary:

```python
>>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, {1:1, 2:2}]}}
>>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, {1:3}]}}
>>> ddiff = DeepDiff(t1, t2)
>>> pprint (ddiff, indent = 2)
{ 'dictionary_item_removed': ["root[4]['b'][2][2]"],
  'values_changed': {"root[4]['b'][2][1]": {'new_value': 3, 'old_value': 1}}}
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
{'values_changed': {'root.y': {'new_value': 23, 'old_value': 22}}}
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
{'values_changed': {'root.b': {'new_value': 2, 'old_value': 1}}}
```

### Object attribute added:

```python
>>> t2.c = "new attribute"
>>> pprint(DeepDiff(t1, t2))
{'attribute_added': ['root.c'],
 'values_changed': {'root.b': {'new_value': 2, 'old_value': 1}}}
```

### Exclude certain types from comparison:
```python
>>> l1 = logging.getLogger("test")
>>> l2 = logging.getLogger("test2")
>>> t1 = {"log": l1, 2: 1337}
>>> t2 = {"log": l2, 2: 1337}
>>> print(DeepDiff(t1, t2, exclude_types={logging.Logger}))
{}
```

### Exclude part of your object tree from comparison:
```python
>>> t1 = {"for life": "vegan", "ingredients": ["no meat", "no eggs", "no dairy"]}
>>> t2 = {"for life": "vegan", "ingredients": ["veggies", "tofu", "soy sauce"]}
>>> print (DeepDiff(t1, t2, exclude_paths={"root['ingredients']"}))
{}
```


## Pycon 2016

I was honored to give a talk about how DeepDiff does what it does at Pycon 2016. Please check out the video and let me know what you think:

[Diff It To Dig It Video](https://www.youtube.com/watch?v=J5r99eJIxF4)
And here is more info: <http://zepworks.com/blog/diff-it-to-digg-it/>


##Documentation

<http://deepdiff.readthedocs.io/en/latest/>

##Changelog

- v2-5-0: Adding ContentHash module to fix ignore_order once and for all.
- v2-1-0: Adding Deep Search. Now you can search for item in an object.
- v2-0-0: Exclusion patterns better coverage. Updating docs.
- v1-8-0: Exclusion patterns.
- v1-7-0: Deep Set comparison.
- v1-6-0: Unifying key names. i.e newvalue is new_value now. For backward compatibility, newvalue still works.
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

## Primary Author

Seperman (Sep Dehpour)

- [Github](https://github.com/seperman)
- [Linkedin](http://www.linkedin.com/in/sepehr)
- [ZepWorks](http://www.zepworks.com)

## Contributors

Thanks to:

- nfvs for Travis-CI setup script.
- brbsix for initial Py3 porting.
- WangFenjin for unicode support.
- timoilya for comparing list of sets when ignoring order.
- Bernhard10 for significant digits comparison.
- b-jazz for PEP257 cleanup, Standardize on full names, fixing line endings.
- [Victor Hahn Castell](http://hahncastell.de) @ [Flexoptix](http://www.flexoptix.net) for deep set comparison and exclusion patterns
