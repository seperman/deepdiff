# DeepDiff v 4.0.2

<!-- ![Downloads](https://img.shields.io/pypi/dm/deepdiff.svg?style=flat) -->
![Python Versions](https://img.shields.io/pypi/pyversions/deepdiff.svg?style=flat)
![Doc](https://readthedocs.org/projects/deepdiff/badge/?version=latest)
![License](https://img.shields.io/pypi/l/deepdiff.svg?version=latest)
[![Build Status](https://travis-ci.org/seperman/deepdiff.svg?branch=master)](https://travis-ci.org/seperman/deepdiff)
[![Coverage Status](https://coveralls.io/repos/github/seperman/deepdiff/badge.svg?branch=master)](https://coveralls.io/github/seperman/deepdiff?branch=master)

- DeepDiff: Deep Difference of dictionaries, iterables, strings and other objects. It will recursively look for all the changes.
- DeepSearch: Search for objects within other objects.
- DeepHash: Hash any object based on their content.

Tested on Python 3.4, 3.5, 3.6, 3.7, Pypy3

**NOTE: Python 2 is not supported any more. DeepDiff v3.3.0 was the last version to support Python 2**


- [Documentation](http://deepdiff.readthedocs.io/en/latest/)


## Installation

### Install from PyPi:

    `pip install deepdiff`

DeepDiff prefers to use Murmur3 for hashing. However you have to manually install Murmur3 by running:

    `pip install mmh3`

Otherwise DeepDiff will be using SHA256 for hashing which is a cryptographic hash and is considerably slower.

If you are running into trouble installing Murmur3, please take a look at the [Troubleshoot](#troubleshoot) section.

### Importing

```python
>>> from deepdiff import DeepDiff  # For Deep Difference of 2 objects
>>> from deepdiff import grep, DeepSearch  # For finding if item exists in an object
>>> from deepdiff import DeepHash  # For hashing objects based on their contents
```

# Deep Diff

DeepDiff gets the difference of 2 objects.

> - Please take a look at the [DeepDiff docs](deepdiff/diff_doc.rst)
> - The full documentation can be found on <https://deepdiff.readthedocs.io>

## Examples

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
>>> ddiff = DeepDiff(t1, t2, ignore_type_in_groups=True)
>>> pprint(ddiff, indent=2)
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


> - Please take a look at the [DeepDiff docs](deepdiff/diff_doc.rst)
> - The full documentation can be found on <https://deepdiff.readthedocs.io>


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

> - Please take a look at the [DeepSearch docs](deepdiff/search_doc.rst)
> - The full documentation can be found on <https://deepdiff.readthedocs.io>

# Deep Hash
(New in v4-0-0)

DeepHash is designed to give you hash of ANY python object based on its contents even if the object is not considered hashable!
DeepHash is supposed to be deterministic in order to make sure 2 objects that contain the same data, produce the same hash.

> - Please take a look at the [DeepHash docs](deepdiff/deephash_doc.rst)
> - The full documentation can be found on <https://deepdiff.readthedocs.io>

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


> - Please take a look at the [DeepHash docs](deepdiff/deephash_doc.rst)
> - The full documentation can be found on <https://deepdiff.readthedocs.io>


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

# Pycon 2016

I was honored to give a talk about how DeepDiff does what it does at Pycon 2016. Please check out the video and let me know what you think:

[Diff It To Dig It Video](https://www.youtube.com/watch?v=J5r99eJIxF4)
And here is more info: <http://zepworks.com/blog/diff-it-to-digg-it/>


# Documentation

<http://deepdiff.readthedocs.io/en/latest/>

# Troubleshoot

## Murmur3

`Failed to build mmh3 when installing DeepDiff`

DeepDiff prefers to use Murmur3 for hashing. However you have to manually install murmur3 by running: `pip install mmh3`

On MacOS Mojave some user experience difficulty when installing Murmur3.

The problem can be solved by running:

    `xcode-select --install`

And then running `pip install mmh3`

# ChangeLog

- v4-0-2: Fixing installation issue where rst files are missing.
- v4-0-1: Fixing installation Tarball missing requirements.txt . DeepDiff v4+ should not show up as pip installable for Py2. Making Murmur3 installation optional.
- v4-0-0: Ending Python 2 support, Adding more functionalities and documentation for DeepHash. Switching to Pytest for testing. Switching to Murmur3 128bit for hashing. Fixing classes which inherit from classes with slots didn't have all of their slots compared. Renaming ContentHash to DeepHash. Adding exclude by path and regex path to DeepHash. Adding ignore_type_in_groups. Adding match_string to DeepSearch. Adding Timedelta object diffing.
- v3-5-0: Exclude regex path
- v3-3-0: Searching for objects and class attributes
- v3-2-2: Adding help(deepdiff)
- v3-2-1: Fixing hash of None
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

# Contribute

1. Please make your PR against the dev branch
2. Please make sure that your PR has tests. Since DeepDiff is used in many sensitive data driven projects, we maintain 100% test coverage on the code. There are occasiannly exceptions to that rule but that is rare.

Thank you!

# Authors

- Seperman (Sep Dehpour)
    - [Github](https://github.com/seperman)
    - [Linkedin](http://www.linkedin.com/in/sepehr)
    - [ZepWorks](http://www.zepworks.com)

- Victor Hahn Castell for major contributions
    - [hahncastell.de](http://hahncastell.de)
    - [flexoptix.net](http://www.flexoptix.net)

- nfvs for Travis-CI setup script.
- brbsix for initial Py3 porting.
- WangFenjin for unicode support.
- timoilya for comparing list of sets when ignoring order.
- Bernhard10 for significant digits comparison.
- b-jazz for PEP257 cleanup, Standardize on full names, fixing line endings.
- finnhughes for fixing __slots__
- moloney for Unicode vs. Bytes default
- serv-inc for adding help(deepdiff)
- movermeyer for updating docs
- maxrothman for search in inherited class attributes
- maxrothman for search for types/objects
- MartyHub for exclude regex paths
- sreecodeslayer for DeepSearch match_string
- Brian Maissy (brianmaissy) for weakref fix, enum tests
- Bartosz Borowik (boba-2) for Exclude types fix when ignoring order
- Brian Maissy (brianmaissy) for fixing classes which inherit from classes with slots didn't have all of their slots compared
- Juan Soler (Soleronline) for adding ignore_type_number
- mthaddon for adding timedelta diffing support
