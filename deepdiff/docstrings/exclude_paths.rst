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
    >>> print (DeepDiff(t1, t2, exclude_paths="ingredients"))  # one item pass it as a string
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


.. _wildcard_paths_label:

Wildcard (Glob) Paths
---------------------

Both ``exclude_paths`` and ``include_paths`` support wildcard patterns for matching multiple paths at once:

- ``[*]`` or ``.*`` matches exactly **one** path segment (any key, index, or attribute).
- ``[**]`` or ``.**`` matches **zero or more** path segments at any depth.

Wildcard patterns must use the full ``root`` prefix (shorthand keys are not supported for wildcards).

Exclude all ``password`` fields regardless of the parent key:
    >>> t1 = {"users": {"alice": {"name": "Alice", "password": "s1"}, "bob": {"name": "Bob", "password": "s2"}}}
    >>> t2 = {"users": {"alice": {"name": "Alice", "password": "x1"}, "bob": {"name": "Bob", "password": "x2"}}}
    >>> DeepDiff(t1, t2, exclude_paths=["root['users'][*]['password']"])
    {}

Include only ``name`` fields at any depth:
    >>> t1 = {"a": {"name": "A", "secret": 1}, "b": {"name": "B", "secret": 2}}
    >>> t2 = {"a": {"name": "X", "secret": 1}, "b": {"name": "Y", "secret": 2}}
    >>> result = DeepDiff(t1, t2, include_paths=["root[*]['name']"])
    >>> set(result.get('values_changed', {}).keys()) == {"root['a']['name']", "root['b']['name']"}
    True

Use ``[**]`` to match at any depth:
    >>> t1 = {"config": {"db": {"password": "old"}, "cache": {"password": "old"}}}
    >>> t2 = {"config": {"db": {"password": "new"}, "cache": {"password": "new"}}}
    >>> DeepDiff(t1, t2, exclude_paths=["root[**]['password']"])
    {}

Literal keys named ``*`` or ``**`` are not treated as wildcards when quoted:
    >>> t1 = {"*": 1, "a": 2}
    >>> t2 = {"*": 10, "a": 20}
    >>> result = DeepDiff(t1, t2, exclude_paths=["root['*']"])
    >>> "root['a']" in result.get('values_changed', {})
    True

When both ``exclude_paths`` and ``include_paths`` apply to the same path, exclusion takes precedence.

Wildcards also work with ``DeepHash`` and ``DeepSearch`` exclude_paths.


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


.. _include_regex_paths_label:

Include Regex Paths
-------------------

This is the counterpart of `exclude_regex_paths`. Pass `include_regex_paths` a set or list of path regexes and only the paths that match one of them are kept in the report. The items in the list could be raw regex strings or compiled regex objects.
    >>> import re
    >>> t1 = [{'a': 1, 'b': 2}, {'c': 4, 'b': 5}]
    >>> t2 = [{'a': 9, 'b': 3}, {'c': 4, 'b': 8}]
    >>> print(DeepDiff(t1, t2, include_regex_paths=r"root\[\d+\]\['b'\]"))
    {'values_changed': {"root[0]['b']": {'new_value': 3, 'old_value': 2}, "root[1]['b']": {'new_value': 8, 'old_value': 5}}}
    >>> include_path = re.compile(r"\['a'\]")
    >>> print(DeepDiff(t1, t2, include_regex_paths=[include_path]))
    {'values_changed': {"root[0]['a']": {'new_value': 9, 'old_value': 1}}}

Just like `exclude_regex_paths`, DeepDiff uses re.search on the path. A regex that matches a parent path keeps that whole subtree, the same way excluding a parent drops its subtree.
    >>> t1 = {"foo": {"bar": "potato", "veg": "x"}, "other": {"z": 1}}
    >>> t2 = {"foo": {"bar": "banana", "veg": "y"}, "other": {"z": 2}}
    >>> print(DeepDiff(t1, t2, include_regex_paths=r"root\['foo'\]$"))
    {'values_changed': {"root['foo']['bar']": {'new_value': 'banana', 'old_value': 'potato'}, "root['foo']['veg']": {'new_value': 'y', 'old_value': 'x'}}}



Back to :doc:`/index`
