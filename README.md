# DeepDiff v 6.1.0

![Downloads](https://img.shields.io/pypi/dm/deepdiff.svg?style=flat)
![Python Versions](https://img.shields.io/pypi/pyversions/deepdiff.svg?style=flat)
![License](https://img.shields.io/pypi/l/deepdiff.svg?version=latest)
[![Build Status](https://github.com/seperman/deepdiff/workflows/Unit%20Tests/badge.svg)](https://github.com/seperman/deepdiff/actions)
[![codecov](https://codecov.io/gh/seperman/deepdiff/branch/master/graph/badge.svg?token=KkHZ3siA3m)](https://codecov.io/gh/seperman/deepdiff)

## DeepDiff Overview

- DeepDiff: Deep Difference of dictionaries, iterables, strings and other objects. It will recursively look for all the changes.
- DeepSearch: Search for objects within other objects.
- DeepHash: Hash any object based on their content.

Tested on Python 3.6+ and PyPy3.

- **[Documentation](https://zepworks.com/deepdiff/6.1.0/)**

## What is new?

DeepDiff 6-1-0

- DeepDiff.affected_paths can be used to get the list of all paths where a change, addition, or deletion was reported for.
- DeepDiff.affected_root_keys can be used to get the list of all paths where a change, addition, or deletion was reported for.  
- Bugfix: ValueError when using Decimal 0.x #339  by [Enric Pou](https://github.com/epou)
- Serialization of UUID 

DeepDiff 6-0-0

- [Exclude obj callback strict](https://github.com/seperman/deepdiff/pull/320/files) parameter is added to DeepDiff by Mikhail Khviyuzov [mskhviyu](https://github.com/mskhviyu).
- A fix for diffing using `iterable_compare_func` with nested objects by [dtorres-sf](https://github.com/dtorres-sf) who originally contributed this feature.
- Temporarily we are publishing DeepDiff under `DeepDiff6` on pypi until further notice.

Note: There are no breaking changes in DeepDiff 6 compared to the latest DeepDiff 5 releases.

## Installation

### Install from PyPi:

`pip install deepdiff6`

If you want to use DeepDiff from commandline:

`pip install "deepdiff6[cli]"`


> Note: Prior to DeepDiff 6, it was published under DeepDiff name on pypi.
> DeepDiff 6 is being published under DeepDiff6 package name on Pypi temporarily until further notice.


### Importing

```python
>>> from deepdiff import DeepDiff  # For Deep Difference of 2 objects
>>> from deepdiff import grep, DeepSearch  # For finding if item exists in an object
>>> from deepdiff import DeepHash  # For hashing objects based on their contents
```

Note: if you want to use DeepDiff via commandline, make sure to run `pip install "deepdiff6[cli]"`. Then you can access the commands via:

- DeepDiff
    - `$ deep diff --help`
- Delta
    - `$ deep patch --help`
- grep
    - `$ deep grep --help`
- extract
    - `$ deep extract --help`

# Deep Diff

DeepDiff gets the difference of 2 objects.

> - Please take a look at the [DeepDiff docs](https://zepworks.com/deepdiff/6.1.0/diff.html)
> - The full documentation of all modules can be found on <https://zepworks.com/deepdiff/6.1.0/>
> - Tutorials and posts about DeepDiff can be found on <https://zepworks.com/tags/deepdiff/>

## A few Examples

> Note: This is just a brief overview of what DeepDiff can do. Please visit <https://zepworks.com/deepdiff/6.1.0/> for full documentation.

### List difference ignoring order or duplicates

```python
>>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
>>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 3, 2, 3]}}
>>> ddiff = DeepDiff(t1, t2, ignore_order=True)
>>> print (ddiff)
{}
```

### Report repetitions

This flag ONLY works when ignoring order is enabled.

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

### Exclude certain types from comparison:

```python
>>> l1 = logging.getLogger("test")
>>> l2 = logging.getLogger("test2")
>>> t1 = {"log": l1, 2: 1337}
>>> t2 = {"log": l2, 2: 1337}
>>> print(DeepDiff(t1, t2, exclude_types={logging.Logger}))
{}
```

### Exclude part of your object tree from comparison

```python
>>> t1 = {"for life": "vegan", "ingredients": ["no meat", "no eggs", "no dairy"]}
>>> t2 = {"for life": "vegan", "ingredients": ["veggies", "tofu", "soy sauce"]}
>>> print (DeepDiff(t1, t2, exclude_paths={"root['ingredients']"}))
{}
```

### Exclude Regex Paths


You can also exclude using regular expressions by using `exclude_regex_paths` and pass a set or list of path regexes to exclude. The items in the list could be raw regex strings or compiled regex objects.

```python
>>> t1 = [{'a': 1, 'b': 2}, {'c': 4, 'b': 5}]
>>> t2 = [{'a': 1, 'b': 3}, {'c': 4, 'b': 5}]
>>> print(DeepDiff(t1, t2, exclude_regex_paths={r"root\[\d+\]\['b'\]"}))
{}
>>> exclude_path = re.compile(r"root\[\d+\]\['b'\]")
>>> print(DeepDiff(t1, t2, exclude_regex_paths=[exclude_path]))
{}
```

### Significant Digits

Digits **after** the decimal point. Internally it uses "{:.Xf}".format(Your Number) to compare numbers where X=significant_digits

```python
>>> t1 = Decimal('1.52')
>>> t2 = Decimal('1.57')
>>> DeepDiff(t1, t2, significant_digits=0)
{}
>>> DeepDiff(t1, t2, significant_digits=1)
{'values_changed': {'root': {'old_value': Decimal('1.52'), 'new_value': Decimal('1.57')}}}
```

### Ignore Type Number - List that contains float and integer:

```py
>>> from deepdiff import DeepDiff
>>> from pprint import pprint
>>> t1 = [1, 2, 3]
>>> t2 = [1.0, 2.0, 3.0]
>>> ddiff = DeepDiff(t1, t2)
>>> pprint(ddiff, indent=2)
{ 'type_changes': { 'root[0]': { 'new_type': <class 'float'>,
                         'new_value': 1.0,
                         'old_type': <class 'int'>,
                         'old_value': 1},
            'root[1]': { 'new_type': <class 'float'>,
                         'new_value': 2.0,
                         'old_type': <class 'int'>,
                         'old_value': 2},
            'root[2]': { 'new_type': <class 'float'>,
                         'new_value': 3.0,
                         'old_type': <class 'int'>,
                         'old_value': 3}}}
>>> ddiff = DeepDiff(t1, t2, ignore_type_in_groups=[(int, float)])
{}
```

## Views

Starting with DeepDiff v 3, there are two different views into your diffed data: text view (original) and tree view (new).

### Text View

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
    Read more about the Tree View at the [tree view section](#tree-view) of this page.


### Tree View

Starting the version v3 You can choose the view into the deepdiff results.
The tree view provides you with tree objects that you can traverse through to find the parents of the objects that are diffed and the actual objects that are being diffed.


#### Value of an item has changed (Tree View)

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

### Serialization

In order to convert the DeepDiff object into a normal Python dictionary, use the to_dict() method.
Note that to_dict will use the text view even if you did the diff in tree view.

Example:

```python
>>> t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3]}}
>>> t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world\n\n\nEnd"}}
>>> ddiff = DeepDiff(t1, t2, view='tree')
>>> ddiff.to_dict()
{'type_changes': {"root[4]['b']": {'old_type': <class 'list'>, 'new_type': <class 'str'>, 'old_value': [1, 2, 3], 'new_value': 'world\n\n\nEnd'}}}
```

In order to do safe json serialization, use the to_json() method.

Example:

```python
>>> t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3]}}
>>> t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world\n\n\nEnd"}}
>>> ddiff = DeepDiff(t1, t2, view='tree')
>>> ddiff.to_json()
'{"type_changes": {"root[4][\'b\']": {"old_type": "list", "new_type": "str", "old_value": [1, 2, 3], "new_value": "world\\n\\n\\nEnd"}}}'
```


> - Please take a look at the [DeepDiff docs](https://zepworks.com/deepdiff/6.1.0/diff.html)
> - The full documentation can be found on <https://zepworks.com/deepdiff/6.1.0/>


# Deep Search

DeepDiff comes with a utility to find the path to the item you are looking for.
It is called DeepSearch and it has a similar interface to DeepDiff.

Let's say you have a huge nested object and want to see if any item with the word `somewhere` exists in it.
Just grep through your objects as you would in shell!

```py
from deepdiff import grep
obj = {"long": "somewhere", "string": 2, 0: 0, "somewhere": "around"}
ds = obj | grep("somewhere")
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

> - Please take a look at the [DeepSearch docs](https://zepworks.com/deepdiff/6.1.0/dsearch.html)
> - The full documentation can be found on <https://zepworks.com/deepdiff/6.1.0/>

# Deep Hash
(New in v4-0-0)

DeepHash is designed to give you hash of ANY python object based on its contents even if the object is not considered hashable!
DeepHash is supposed to be deterministic in order to make sure 2 objects that contain the same data, produce the same hash.

> - Please take a look at the [DeepHash docs](https://zepworks.com/deepdiff/6.1.0/deephash.html)
> - The full documentation can be found on <https://zepworks.com/deepdiff/6.1.0/>

Let's say you have a dictionary object.

```py
>>> from deepdiff import DeepHash
>>>
>>> obj = {1: 2, 'a': 'b'}
```

If you try to hash it:

```py
>>> hash(obj)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: unhashable type: 'dict'
```

But with DeepHash:

```py
>>> from deepdiff import DeepHash
>>> obj = {1: 2, 'a': 'b'}
>>> DeepHash(obj)
{4355639248: 2468916477072481777512283587789292749, 4355639280: -35787773492556653776377555218122431491, 4358636128: -88390647972316138151822486391929534118, 4358009664: 8833996863197925870419376694314494743, 4357467952: 34150898645750099477987229399128149852}
```

So what is exactly the hash of obj in this case?
DeepHash is calculating the hash of the obj and any other object that obj contains.
The output of DeepHash is a dictionary of object IDs to their hashes.
In order to get the hash of obj itself, you need to use the object (or the id of object) to get its hash:

```py
>>> hashes = DeepHash(obj)
>>> hashes[obj]
34150898645750099477987229399128149852
```

Which you can write as:

```py
>>> hashes = DeepHash(obj)[obj]
```

At first it might seem weird why DeepHash(obj)[obj] but remember that DeepHash(obj) is a dictionary of hashes of all other objects that obj contains too.


> - Please take a look at the [DeepHash docs](https://zepworks.com/deepdiff/6.1.0/deephash.html)
> - The full documentation can be found on <https://zepworks.com/deepdiff/6.1.0/>


# Using DeepDiff in unit tests

`result` is the output of the function that is being tests.
`expected` is the expected output of the function.

```python
self.assertEqual(DeepDiff(expected, result), {})
```

or if you are using Pytest:


```python
assert not DeepDiff(expected, result)
```

In other words, assert that there is no diff between the expected and the result.

# Difference with Json Patch

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


# Documentation

<https://zepworks.com/deepdiff/current/>


# Pycon 2016

I was honored to give a talk about the basics of how DeepDiff does what it does at Pycon 2016. Please check out the video and let me know what you think:

[Diff It To Dig It Video](https://www.youtube.com/watch?v=J5r99eJIxF4)
And here is more info: <http://zepworks.com/blog/diff-it-to-digg-it/>

# ChangeLog

Please take a look at the [CHANGELOG](CHANGELOG.md) file.

# Releases

We use bump2version to bump and tag releases.

```bash
git checkout master && git pull
bumpversion {patch|minor|major}
git push && git push --tags
```

# Contribute

1. Please make your PR against the dev branch
2. Please make sure that your PR has tests. Since DeepDiff is used in many sensitive data driven projects, we strive to maintain around 100% test coverage on the code.

Please run `pytest --cov=deepdiff --runslow` to see the coverage report. Note that the `--runslow` flag will run some slow tests too. In most cases you only want to run the fast tests which so you wont add the `--runslow` flag.

Or to see a more user friendly version, please run: `pytest --cov=deepdiff --cov-report term-missing --runslow`.

Thank you!

# Citing

How to cite this library (APA style):

    Dehpour, S. (2022). DeepDiff (Version 6.1.0) [Software]. Available from https://github.com/seperman/deepdiff.

How to cite this library (Chicago style):

    Dehpour, Sep. 2022. DeepDiff (version 6.1.0).

# Authors

Please take a look at the [AUTHORS](AUTHORS.md) file.
