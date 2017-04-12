# deepdiff v 3.2.0

<!-- ![Downloads](https://img.shields.io/pypi/dm/deepdiff.svg?style=flat) -->
![Python Versions](https://img.shields.io/pypi/pyversions/deepdiff.svg?style=flat)
![Doc](https://readthedocs.org/projects/deepdiff/badge/?version=latest)
![License](https://img.shields.io/pypi/l/deepdiff.svg?version=latest)
[![Build Status](https://travis-ci.org/seperman/deepdiff.svg?branch=master)](https://travis-ci.org/seperman/deepdiff)
[![Coverage Status](https://coveralls.io/repos/github/seperman/deepdiff/badge.svg?branch=master)](https://coveralls.io/github/seperman/deepdiff?branch=master)

Deep Difference of dictionaries, iterables, strings and other objects. It will recursively look for all the changes.
Tested on Python 2.7, 3.3, 3.4, 3.5, 3.6, Pypy, Pypy3

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
- [Views](#views)
- [Text View](#text-view)
- [Tree View](#tree-view)
- [Serialization](#serialization)
- [Documentation](http://deepdiff.readthedocs.io/en/latest/)


## Installation

### Install from PyPi:

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

Tip: Take a look at [grep](#grep) which gives you a new interface for DeepSearch!

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

## Grep
(New in v3-2-0)

Grep is another interface for DeepSearch.
Just grep through your objects as you would in shell!

```py
from deepdiff import grep
obj = {"long": "somewhere", "string": 2, 0: 0, "somewhere": "around"}
ds = obj | grep(item)
print(ds)
```

Which will print:

```py
{'matched_paths': {"root['somewhere']"},
 'matched_values': {"root['long']"}}
```

And you can pass all the same kwargs as DeepSearch to grep too:

```py
>>> obj | grep(item, verbose_level=2)
{'matched_paths': {"root['somewhere']": 'around'}, 'matched_values': {"root['long']": 'somewhere'}}
```

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

# Views

Starting with DeepDiff v 3, there are two different views into your diffed data: text view (original) and tree view (new).

## Text View

Text view is the original and currently the default view of DeepDiff.

It is called text view because the results contain texts that represent the path to the data:

Example of using the text view.

```python
>>> from deepdiff import DeepDiff
>>> t1 = {1:1, 3:3, 4:4}
>>> t2 = {1:1, 3:3, 5:5, 6:6}
>>> ddiff = DeepDiff(t1, t2)
>>> print(ddiff)
{'dictionary_item_added': {'root[5]', 'root[6]'}, 'dictionary_item_removed': {'root[4]'}}
```

So for example `ddiff['dictionary_item_removed']` is a set if strings thus this is called the text view.

    The following examples are using the *default text view.*
    The Tree View is introduced in DeepDiff v3
    and provides traversing capabilities through your diffed data and more!
    Read more about the Tree View at the bottom of this page.


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


    All the examples for the text view work for the tree view too. You just need to set view='tree' to get it in tree form.


## Tree View

Starting the version v3 You can choose the view into the deepdiff results.
The tree view provides you with tree objects that you can traverse through to find the parents of the objects that are diffed and the actual objects that are being diffed.

This view is very useful when dealing with nested objects.
Note that tree view always returns results in the form of Python sets.

You can traverse through the tree elements!

    The Tree view is just a different representation of the diffed data.
    Behind the scene, DeepDiff creates the tree view first and then converts it to textual representation for the text view.

```
+---------------------------------------------------------------+
|                                                               |
|    parent(t1)              parent node            parent(t2)  |
|      +                          ^                     +       |
+------|--------------------------|---------------------|-------+
       |                      |   | up                  |
       | Child                |   |                     | ChildRelationship
       | Relationship         |   |                     |
       |                 down |   |                     |
+------|----------------------|-------------------------|-------+
|      v                      v                         v       |
|    child(t1)              child node               child(t2)  |
|                                                               |
+---------------------------------------------------------------+
```

 - up -  Move up to the parent node
 - down -  Move down to the child node
 - path() -  Get the path to the current node
 - t1 -  The first item in the current node that is being diffed
 - t2 -  The second item in the current node that is being diffed
 - additional -  Additional information about the node i.e. repetition
 - repetition -  Shortcut to get the repetition report


The tree view allows you to have more than mere textual representaion of the diffed objects.
It gives you the actual objects (t1, t2) throughout the tree of parents and children.

## Examples - Tree View

    The Tree View is introduced in DeepDiff v3
    Set view='tree' in order to use this view.

### Value of an item has changed (Tree View)

```python
>>> from deepdiff import DeepDiff
>>> from pprint import pprint
>>> t1 = {1:1, 2:2, 3:3}
>>> t2 = {1:1, 2:4, 3:3}
>>> ddiff_verbose0 = DeepDiff(t1, t2, verbose_level=0, view='tree')
>>> ddiff_verbose0
{'values_changed': {<root[2]>}}
>>>
>>> ddiff_verbose1 = DeepDiff(t1, t2, verbose_level=1, view='tree')
>>> ddiff_verbose1
{'values_changed': {<root[2] t1:2, t2:4>}}
>>> set_of_values_changed = ddiff_verbose1['values_changed']
>>> # since set_of_values_changed includes only one item in a set
>>> # in order to get that one item we can:
>>> (changed,) = set_of_values_changed
>>> changed  # Another way to get this is to do: changed=list(set_of_values_changed)[0]
<root[2] t1:2, t2:4>
>>> changed.t1
2
>>> changed.t2
4
>>> # You can traverse through the tree, get to the parents!
>>> changed.up
<root t1:{1: 1, 2: 2,...}, t2:{1: 1, 2: 4,...}>
```

### List difference (Tree View)

```python
>>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3, 4]}}
>>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2]}}
>>> ddiff = DeepDiff(t1, t2, view='tree')
>>> ddiff
{'iterable_item_removed': {<root[4]['b'][3] t1:4, t2:Not Present>, <root[4]['b'][2] t1:3, t2:Not Present>}}
>>> # Note that the iterable_item_removed is a set. In this case it has 2 items in it.
>>> # One way to get one item from the set is to convert it to a list
>>> # And then get the first item of the list:
>>> removed = list(ddiff['iterable_item_removed'])[0]
>>> removed
<root[4]['b'][2] t1:3, t2:Not Present>
>>>
>>> parent = removed.up
>>> parent
<root[4]['b'] t1:[1, 2, 3, 4], t2:[1, 2]>
>>> parent.path()
"root[4]['b']"
>>> parent.t1
[1, 2, 3, 4]
>>> parent.t2
[1, 2]
>>> parent.up
<root[4] t1:{'a': 'hello...}, t2:{'a': 'hello...}>
>>> parent.up.up
<root t1:{1: 1, 2: 2,...}, t2:{1: 1, 2: 2,...}>
>>> parent.up.up.t1
{1: 1, 2: 2, 3: 3, 4: {'a': 'hello', 'b': [1, 2, 3, 4]}}
>>> parent.up.up.t1 == t1  # It is holding the original t1 that we passed to DeepDiff
True
```

### List difference 2  (Tree View)

```python
>>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
>>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 3, 2, 3]}}
>>> ddiff = DeepDiff(t1, t2, view='tree')
>>> pprint(ddiff, indent = 2)
{ 'iterable_item_added': {<root[4]['b'][3] t1:Not Present, t2:3>},
  'values_changed': { <root[4]['b'][1] t1:2, t2:3>,
                      <root[4]['b'][2] t1:3, t2:2>}}
>>>
>>> # Note that iterable_item_added is a set with one item.
>>> # So in order to get that one item from it, we can do:
>>>
>>> (added,) = ddiff['iterable_item_added']
>>> added
<root[4]['b'][3] t1:Not Present, t2:3>
>>> added.up.up
<root[4] t1:{'a': 'hello...}, t2:{'a': 'hello...}>
>>> added.up.up.path()
'root[4]'
>>> added.up.up.down
<root[4]['b'] t1:[1, 2, 3], t2:[1, 3, 2, 3]>
>>>
>>> # going up twice and then down twice gives you the same node in the tree:
>>> added.up.up.down.down == added
True
```

### List difference ignoring order but reporting repetitions (Tree View)

```python
>>> t1 = [1, 3, 1, 4]
>>> t2 = [4, 4, 1]
>>> ddiff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True, view='tree')
>>> pprint(ddiff, indent=2)
{ 'iterable_item_removed': {<root[1] t1:3, t2:Not Present>},
  'repetition_change': { <root[3] {'repetition': {'old_repeat': 1,...}>,
                         <root[0] {'repetition': {'old_repeat': 2,...}>}}
>>>
>>> # repetition_change is a set with 2 items.
>>> # in order to get those 2 items, we can do the following.
>>> # or we can convert the set to list and get the list items.
>>> # or we can iterate through the set items
>>>
>>> (repeat1, repeat2) = ddiff['repetition_change']
>>> repeat1  # the default verbosity is set to 1.
<root[0] {'repetition': {'old_repeat': 2,...}>
>>> # The actual data regarding the repetitions can be found in the repetition attribute:
>>> repeat1.repetition
{'old_repeat': 1, 'new_repeat': 2, 'old_indexes': [3], 'new_indexes': [0, 1]}
>>>
>>> # If you change the verbosity, you will see less:
>>> ddiff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True, view='tree', verbose_level=0)
>>> ddiff
{'repetition_change': {<root[3]>, <root[0]>}, 'iterable_item_removed': {<root[1]>}}
>>> (repeat1, repeat2) = ddiff['repetition_change']
>>> repeat1
<root[0]>
>>>
>>> # But the verbosity level does not change the actual report object.
>>> # It only changes the textual representaion of the object. We get the actual object here:
>>> repeat1.repetition
{'old_repeat': 1, 'new_repeat': 2, 'old_indexes': [3], 'new_indexes': [0, 1]}
>>> repeat1.t1
4
>>> repeat1.t2
4
>>> repeat1.up
<root>
```

### List that contains dictionary (Tree View)

```python
>>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, {1:1, 2:2}]}}
>>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, {1:3}]}}
>>> ddiff = DeepDiff(t1, t2, view='tree')
>>> pprint (ddiff, indent = 2)
{ 'dictionary_item_removed': {<root[4]['b'][2][2] t1:2, t2:Not Present>},
  'values_changed': {<root[4]['b'][2][1] t1:1, t2:3>}}

Sets (Tree View):
>>> t1 = {1, 2, 8}
>>> t2 = {1, 2, 3, 5}
>>> ddiff = DeepDiff(t1, t2, view='tree')
>>> print(ddiff)
{'set_item_removed': {<root: t1:8, t2:Not Present>}, 'set_item_added': {<root: t1:Not Present, t2:5>, <root: t1:Not Present, t2:3>}}
>>> # grabbing one item from set_item_removed set which has one item only
>>> (item,) = ddiff['set_item_removed']
>>> item.up
<root t1:{8, 1, 2}, t2:{1, 2, 3, 5}>
>>> item.up.t1 == t1
True
```

### Named Tuples (Tree View):

```python
>>> from collections import namedtuple
>>> Point = namedtuple('Point', ['x', 'y'])
>>> t1 = Point(x=11, y=22)
>>> t2 = Point(x=11, y=23)
>>> print(DeepDiff(t1, t2, view='tree'))
{'values_changed': {<root.y t1:22, t2:23>}}
```

### Custom objects (Tree View):

```python
>>> class ClassA(object):
...     a = 1
...     def __init__(self, b):
...         self.b = b
...
>>> t1 = ClassA(1)
>>> t2 = ClassA(2)
>>>
>>> print(DeepDiff(t1, t2, view='tree'))
{'values_changed': {<root.b t1:1, t2:2>}}
```

### Object attribute added (Tree View):

```python
>>> t2.c = "new attribute"
>>> pprint(DeepDiff(t1, t2, view='tree'))
{'attribute_added': {<root.c t1:Not Present, t2:'new attribute'>},
 'values_changed': {<root.b t1:1, t2:2>}}
```

### Approximate decimals comparison (Significant digits after the point) (Tree View):

```python
>>> t1 = Decimal('1.52')
>>> t2 = Decimal('1.57')
>>> DeepDiff(t1, t2, significant_digits=0, view='tree')
{}
>>> ddiff = DeepDiff(t1, t2, significant_digits=1, view='tree')
>>> ddiff
{'values_changed': {<root t1:Decimal('1.52'), t2:Decimal('1.57')>}}
>>> (change1,) = ddiff['values_changed']
>>> change1
<root t1:Decimal('1.52'), t2:Decimal('1.57')>
>>> change1.t1
Decimal('1.52')
>>> change1.t2
Decimal('1.57')
>>> change1.path()
'root'
```

### Approximate float comparison (Significant digits after the point) (Tree View):

```python
>>> t1 = [ 1.1129, 1.3359 ]
>>> t2 = [ 1.113, 1.3362 ]
>>> ddiff = DeepDiff(t1, t2, significant_digits=3, view='tree')
>>> ddiff
{}
>>> ddiff = DeepDiff(t1, t2, view='tree')
>>> pprint(ddiff, indent=2)
{ 'values_changed': { <root[0] t1:1.1129, t2:1.113>,
                      <root[1] t1:1.3359, t2:1.3362>}}
>>> ddiff = DeepDiff(1.23*10**20, 1.24*10**20, significant_digits=1, view='tree')
>>> ddiff
{'values_changed': {<root t1:1.23e+20, t2:1.24e+20>}}
```

    All the examples for the text view work for the tree view too. You just need to set view='tree' to get it in tree form.

## Serialization

DeepDiff uses jsonpickle in order to serialize and deserialize its results into json. This works for both tree view and text view.

### Serialize and then deserialize back to deepdiff

```python
>>> t1 = {1: 1, 2: 2, 3: 3}
>>> t2 = {1: 1, 2: "2", 3: 3}
>>> ddiff = DeepDiff(t1, t2)
>>> jsoned = ddiff.json
>>> jsoned
'{"type_changes": {"root[2]": {"py/object": "deepdiff.helper.RemapDict", "new_type": {"py/type": "__builtin__.str"}, "new_value": "2", "old_type": {"py/type": "__builtin__.int"}, "old_value": 2}}}'
>>> ddiff_new = DeepDiff.from_json(jsoned)
>>> ddiff == ddiff_new
True
```

## Pycon 2016

I was honored to give a talk about how DeepDiff does what it does at Pycon 2016. Please check out the video and let me know what you think:

[Diff It To Dig It Video](https://www.youtube.com/watch?v=J5r99eJIxF4)
And here is more info: <http://zepworks.com/blog/diff-it-to-digg-it/>


##Documentation

<http://deepdiff.readthedocs.io/en/latest/>

##Changelog

- v3-2-0: Adding grep for search: object | grep(item)
- v3-1-3: Unicode vs. Bytes default fix
- v3-1-2: NotPresent Fix when item is added or removed.
- v3-1-1: Bug fix when item value is None (#58)
- v3-1-0: Serialization to/from json
- v3-0-0: Introducing Tree View
- v2-5-3: Bug fix on logging for content hash.
- v2-5-2: Bug fixes on content hash.
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

## Authors

Seperman (Sep Dehpour)

- [Github](https://github.com/seperman)
- [Linkedin](http://www.linkedin.com/in/sepehr)
- [ZepWorks](http://www.zepworks.com)

Victor Hahn Castell

- [hahncastell.de](http://hahncastell.de)
- [flexoptix.net](http://www.flexoptix.net)

Also thanks to:

- nfvs for Travis-CI setup script.
- brbsix for initial Py3 porting.
- WangFenjin for unicode support.
- timoilya for comparing list of sets when ignoring order.
- Bernhard10 for significant digits comparison.
- b-jazz for PEP257 cleanup, Standardize on full names, fixing line endings.
- finnhughes for fixing __slots__
- moloney for Unicode vs. Bytes default
