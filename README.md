# deepdiff v 0.6.0

![Doc](https://readthedocs.org/projects/deepdiff/badge/?version=latest)

Deep Difference of dictionaries, iterables, strings and other objects. It will recursively look for all the changes.
Tested on Python 2.7 and 3.4

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

### Same object returns empty

```python
>>> t1 = {1:1, 2:2, 3:3}
>>> t2 = t1
>>> ddiff = DeepDiff(t1, t2)
>>> ddiff
{}
```

### Type of an item has changed

```python
>>> t1 = {1:1, 2:2, 3:3}
>>> t2 = {1:1, 2:"2", 3:3}
>>> ddiff = DeepDiff(t1, t2)
>>> print (ddiff)
{'type_changes': ["root[2]: 2=<type 'int'> ===> 2=<type 'str'>"]}
```

### Value of an item has changed

```python
>>> t1 = {1:1, 2:2, 3:3}
>>> t2 = {1:1, 2:4, 3:3}
>>> ddiff = DeepDiff(t1, t2)
>>> print (ddiff)
{'values_changed': ['root[2]: 2 ===> 4']}
```

### Item added and/or removed

```python
>>> t1 = {1:1, 2:2, 3:3, 4:4}
>>> t2 = {1:1, 2:4, 3:3, 5:5, 6:6}
>>> ddiff = DeepDiff(t1, t2)
>>> pprint (ddiff)
{'dic_item_added': ['root[5, 6]'],
 'dic_item_removed': ['root[4]'],
 'values_changed': ['root[2]: 2 ===> 4']}
```

### String difference

```python
>>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":"world"}}
>>> t2 = {1:1, 2:4, 3:3, 4:{"a":"hello", "b":"world!"}}
>>> ddiff = DeepDiff(t1, t2)
>>> from pprint import pprint
>>> pprint (ddiff, indent = 2)
{ 'values_changed': [ 'root[2]: 2 ===> 4',
                      "root[4]['b']: 'world' ===> 'world!'"]}
>>>
>>> print (ddiff['values_changed'][1])
root[4]['b']: 'world' ===> 'world!'
```

###String difference 2

```python
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
```

### Type change

```python
>>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
>>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":"world\n\n\nEnd"}}
>>> ddiff = DeepDiff(t1, t2)
>>> pprint (ddiff, indent = 2)
{ 'type_changes': [ "root[4]['b']: [1, 2, 3]=<type 'list'> ===> world\n"
                    '\n'
                    '\n'
                    "End=<type 'str'>"]}
```

### List difference

```python
>>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
>>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2]}}
>>> ddiff = DeepDiff(t1, t2)
>>> pprint (ddiff, indent = 2)
{'iterable_item_removed': ["root[4]['b']: [3]"]}
```

### List difference 2

```python
>>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
>>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 3, 2, 3]}}
>>> ddiff = DeepDiff(t1, t2)
>>> pprint (ddiff, indent = 2)
{ 'iterable_item_added': ["root[4]['b']: [3]"],
  'values_changed': ["root[4]['b'][1]: 2 ===> 3", "root[4]['b'][2]: 3 ===> 2"]}
```

### List that contains dictionary:

```python
>>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, {1:1, 2:2}]}}
>>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, {1:3}]}}
>>> ddiff = DeepDiff(t1, t2)
>>> pprint (ddiff, indent = 2)
{ 'dic_item_removed': ["root[4]['b'][2][2]"],
  'values_changed': ["root[4]['b'][2][1]: 1 ===> 3"]}
```

### Sets

```python
>>> t1 = {1, 2, 8}
>>> t2 = {1, 2, 3, 5}
>>> ddiff = DeepDiff(t1, t2)
>>> print (DeepDiff(t1, t2))
{'set_item_added': ['root: [3, 5]'], 'set_item_removed': ['root: [8]']}
```

### Named Tuples:

```python
>>> from collections import namedtuple
>>> Point = namedtuple('Point', ['x', 'y'])
>>> t1 = Point(x=11, y=22)
>>> t2 = Point(x=11, y=23)
>>> print (DeepDiff(t1, t2))
{'values_changed': ['root.y: 22 ===> 23']}
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
>>> print(DeepDiff(t1, t2))
{'values_changed': ['root.b: 1 ===> 2']}
```

### Object attribute added:

```python
>>> t2.c = "new attribute"
>>> print(DeepDiff(t1, t2))
{'attribute_added': ['root.c'], 'values_changed': ['root.b: 1 ===> 2']}
```

### Ignoring order:

**Note: If your objects include iterable containing any unhashable item, ignoring the order can be expensive.**

```python
>>> t1 = [{"a": 2}, {"b": [3, 4, {1: 1}]}]
>>> t2 = [{"b": [3, 4, {1: 1}]}, {"a": 2}]
ddiff = DeepDiff(t1, t2, ignore_order=True)
>>>
>>> print(DeepDiff(t1, t2))
{}
```

##Documentation

<http://deepdiff.readthedocs.org/en/latest/>

##Changelog

- v0-6-0: Adding unicode support
- v0-5-9: Adding decimal support
- v0-5-8: Adding ignore order of unhashables support
- v0-5-7: Adding ignore order support
- v0-5-6: Adding slots support
- v0-5-5: Adding loop detection

##Author

Seperman

Github:  <https://github.com/seperman>
Linkedin:  <http://www.linkedin.com/in/sepehr>
ZepWorks:   <http://www.zepworks.com>

Thanks to:
brbsix for initial Py3 porting
WangFenjin for unicode support

