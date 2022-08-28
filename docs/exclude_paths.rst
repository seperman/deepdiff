:doc:`/index`

.. _exclude_paths_label:

Exclude Paths
=============

Exclude part of your object tree from comparison.
use exclude_paths and pass a set or list of paths to exclude, if only one item is being passed, then just put it there as a string. No need to pass it as a list then.

Example
    >>> t1 = {"for life": "vegan", "ingredients": ["no meat", "no eggs", "no dairy"]}
    >>> t2 = {"for life": "vegan", "ingredients": ["veggies", "tofu", "soy sauce"]}
    >>> print (DeepDiff(t1, t2, exclude_paths="root['ingredients']"))  # one item pass it as a string
    {}
    >>> print (DeepDiff(t1, t2, exclude_paths=["root['ingredients']", "root['ingredients2']"]))  # multiple items pass as a list or a set.
    {}

Also for root keys you don't have to pass as "root['key']". You can instead just pass the key:

Example
    >>> t1 = {"for life": "vegan", "ingredients": ["no meat", "no eggs", "no dairy"]}
    >>> t2 = {"for life": "vegan", "ingredients": ["veggies", "tofu", "soy sauce"]}
    >>> print (DeepDiff(t1, t2, exclude_paths="ingredients))  # one item pass it as a string
    {}
    >>> print (DeepDiff(t1, t2, exclude_paths=["ingredients", "ingredients2"]))  # multiple items pass as a list or a set.
    {}


.. _include_paths_label:

Include Paths
=============

Only include this part of your object tree in the comparison.
Use include_paths and pass a set or list of paths to limit diffing to only those paths. If only one item is being passed, just put it there as a string—no need to pass it as a list then.

Example
    >>> t1 = {"for life": "vegan", "ingredients": ["no meat", "no eggs", "no dairy"]}
    >>> t2 = {"for life": "vegan", "ingredients": ["veggies", "tofu", "soy sauce"]}
    >>> print (DeepDiff(t1, t2, include_paths="root['for life']"))  # one item pass it as a string
    {}
    >>> print (DeepDiff(t1, t2, include_paths=["for life", "ingredients2"]))  # multiple items pass as a list or a set and you don't need to pass the full path when dealing with root keys. So instead of "root['for life']" you can pass "for life"
    {}


When passing include_paths, all the children of that path will be included too.

Example
    >>> t1 = {
    ...     "foo": {"bar": "potato"},
    ...     "ingredients": ["no meat", "no eggs", "no dairy"]
    ... }
    >>> t2 = {
    ...     "foo": {"bar": "banana"},
    ...     "ingredients": ["bread", "cheese"]
    ... }
    >>> DeepDiff(t1, t2, include_paths="foo")
    {'values_changed': {"root['foo']['bar']": {'new_value': 'banana', 'old_value': 'potato'}}}


.. _exclude_regex_paths_label:

Exclude Regex Paths
-------------------

You can also exclude using regular expressions by using `exclude_regex_paths` and pass a set or list of path regexes to exclude. The items in the list could be raw regex strings or compiled regex objects.
    >>> import re
    >>> t1 = [{'a': 1, 'b': 2}, {'c': 4, 'b': 5}]
    >>> t2 = [{'a': 1, 'b': 3}, {'c': 4, 'b': 5}]
    >>> print(DeepDiff(t1, t2, exclude_regex_paths=r"root\[\d+\]\['b'\]"))
    {}
    >>> exclude_path = re.compile(r"root\[\d+\]\['b'\]")
    >>> print(DeepDiff(t1, t2, exclude_regex_paths=[exclude_path]))
    {}

example 2:
    >>> t1 = {'a': [1, 2, [3, {'foo1': 'bar'}]]}
    >>> t2 = {'a': [1, 2, [3, {'foo2': 'bar'}]]}
    >>> DeepDiff(t1, t2, exclude_regex_paths="\['foo.'\]")  # since it is one item in exclude_regex_paths, you don't have to put it in a list or a set.
    {}

Tip: DeepDiff is using re.search on the path. So if you want to force it to match from the beginning of the path, add `^` to the beginning of regex.



Back to :doc:`/index`
