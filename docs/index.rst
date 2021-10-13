.. DeepDiff documentation master file, created by
   sphinx-quickstart on Mon Jul 20 06:06:44 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


DeepDiff 5.6.0 documentation!
=============================

*****************
DeepDiff Overview
*****************

The DeepDiff library includes the following modules:

- **DeepDiff** For Deep Difference of 2 objects. :doc:`/diff`

    It return the deep Difference of python objects. It can also be used to take the distance between objects. :doc:`/deep_distance`

- **DeepSearch** Search for objects within other objects. :doc:`/dsearch`

- **DeepHash** Hash any object based on their content even if they are not "hashable" in Python's eyes.  :doc:`/deephash`

- **Delta** Delta of objects that can be applied to other objects. Imagine git commits but for structured data.  :doc:`/delta`

- **Extract** For extracting a path from an object  :doc:`/extract`

- **Commandline** Most of the above functionality is also available via the commandline module  :doc:`/commandline`

*************************
Supported Python Versions
*************************

DeepDiff is rigorously tested against Python 3.6 up to 3.10 and Pypy3

NOTE: Python 2 is not supported any more. DeepDiff v3.3.0 was the last version to supprt Python 2.

***********
What is New
***********

## What is new?

New In DeepDiff 5-6-0
---------------------

**Create custom operators!**

    >>> from deepdiff import DeepDiff
    >>> from deepdiff.operator import BaseOperator
    >>> class CustomClass:
    ...     def __init__(self, d: dict, l: list):
    ...         self.dict = d
    ...         self.dict['list'] = l
    ...
    >>>
    >>> custom1 = CustomClass(d=dict(a=1, b=2), l=[1, 2, 3])
    >>> custom2 = CustomClass(d=dict(c=3, d=4), l=[1, 2, 3, 2])
    >>> custom3 = CustomClass(d=dict(a=1, b=2), l=[1, 2, 3, 4])
    >>>
    >>>
    >>> class ListMatchOperator(BaseOperator):
    ...     def give_up_diffing(self, level, diff_instance):
    ...         if set(level.t1.dict['list']) == set(level.t2.dict['list']):
    ...             return True
    ...
    >>>
    >>> DeepDiff(custom1, custom2, custom_operators=[
    ...     ListMatchOperator(types=[CustomClass])
    ... ])
    {}
    >>>
    >>>
    >>> DeepDiff(custom2, custom3, custom_operators=[
    ...     ListMatchOperator(types=[CustomClass])
    ... ])
    {'dictionary_item_added': [root.dict['a'], root.dict['b']], 'dictionary_item_removed': [root.dict['c'], root.dict['d']], 'values_changed': {"root.dict['list'][3]": {'new_value': 4, 'old_value': 2}}}
    >>>


**New in 5-6-0: Dynamic ignore order function**

Ignoring order when certain word in the path

    >>> from deepdiff import DeepDiff
    >>> t1 = {'a': [1, 2], 'b': [3, 4]}
    >>> t2 = {'a': [2, 1], 'b': [4, 3]}
    >>> DeepDiff(t1, t2, ignore_order=True)
    {}
    >>> def ignore_order_func(level):
    ...     return 'a' in level.path()
    ...
    >>> DeepDiff(t1, t2, ignore_order=True, ignore_order_func=ignore_order_func)
    {'values_changed': {"root['b'][0]": {'new_value': 4, 'old_value': 3}, "root['b'][1]": {'new_value': 3, 'old_value': 4}}}



New In DeepDiff 5-5-0
---------------------

1. New option called `iterable_compare_func` that takes a function pointer to compare two items. The function takes three parameters (x, y, level) and should return `True` if it is a match, `False` if it is not a match or raise `CannotCompare` if it is unable to compare the two. If `CannotCompare` is raised then it will revert back to comparing in order. If `iterable_compare_func` is not provided or set to None the behavior defaults to comparing items in order. A new report item called `iterable_item_moved` this will only ever be added if there is a custom compare function.

    >>> from deepdiff import DeepDiff
    >>> from deepdiff.helper import CannotCompare
    >>>
    >>> t1 = [
    ...     {
    ...         'id': 2,
    ...         'value': [7, 8, 1]
    ...     },
    ...     {
    ...         'id': 3,
    ...         'value': [7, 8],
    ...     },
    ... ]
    >>>
    >>> t2 = [
    ...     {
    ...         'id': 2,
    ...         'value': [7, 8]
    ...     },
    ...     {
    ...         'id': 3,
    ...         'value': [7, 8, 1],
    ...     },
    ... ]
    >>>
    >>> DeepDiff(t1, t2)
    {'values_changed': {"root[0]['id']": {'new_value': 2, 'old_value': 1}, "root[0]['value'][0]": {'new_value': 7, 'old_value': 1}, "root[1]['id']": {'new_value': 3, 'old_value': 2}, "root[2]['id']": {'new_value': 1, 'old_value': 3}, "root[2]['value'][0]": {'new_value': 1, 'old_value': 7}}, 'iterable_item_added': {"root[0]['value'][1]": 8}, 'iterable_item_removed': {"root[2]['value'][1]": 8}}

Now let's use the custom compare function to guide DeepDiff in what to compare with what:

    >>> def compare_func(x, y, level=None):
    ...     try:
    ...         return x['id'] == y['id']
    ...     except Exception:
    ...         raise CannotCompare() from None
    ...
    >>> DeepDiff(t1, t2, iterable_compare_func=compare_func)
    {'iterable_item_added': {"root[2]['value'][2]": 1}, 'iterable_item_removed': {"root[1]['value'][2]": 1}}

2. You can get the path() of item in the tree view in the list format instead of string representation by passing path(output_format='list')

.. code:: python

    >>> from deepdiff import DeepDiff
    >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3, 4]}}
    >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2]}}
    >>> ddiff = DeepDiff(t1, t2, view='tree')
    >>> ddiff
    {'iterable_item_removed': [<root[4]['b'][2] t1:3, t2:not present>, <root[4]['b'][3] t1:4, t2:not present>]}
    >>> removed = ddiff['iterable_item_removed'][0]
    >>> removed.path()
    "root[4]['b'][2]"
    >>> removed.path(output_format='list')
    [4, 'b', 2]


New In Deepdiff 5.3.0
---------------------

Deepdiff 5.3.0 comes with regular expressions in the DeepSearch and grep modules:


.. code:: python

    >>> from deepdiff import grep
    >>> from pprint import pprint
    >>> obj = ["something here", {"long": "somewhere", "someone": 2, 0: 0, "somewhere": "around"}]
    >>> ds = obj | grep("some.*", use_regexp=True)
    { 'matched_paths': ["root[1]['someone']", "root[1]['somewhere']"],
      'matched_values': ['root[0]', "root[1]['long']"]}


*********
Tutorials
*********

Tutorials can be found on `Zepworks blog <https://zepworks.com/tags/deepdiff/>`_

************
Installation
************

Install from PyPi::

    pip install deepdiff

If you want to use DeepDiff from commandline::

    pip install "deepdiff[cli]"

Read about DeepDiff optimizations at :ref:`optimizations_label`


Importing
~~~~~~~~~

.. code:: python

    >>> from deepdiff import DeepDiff  # For Deep Difference of 2 objects
    >>> from deepdiff import grep, DeepSearch  # For finding if item exists in an object
    >>> from deepdiff import DeepHash  # For hashing objects based on their contents
    >>> from deepdiff import Delta  # For creating delta of objects that can be applied later to other objects.
    >>> from deepdiff import extract  # For extracting a path from an object


Note: if you want to use DeepDiff via commandline, make sure to run:: 
    pip install "deepdiff[cli]"

Then you can access the commands via:

- DeepDiff

.. code:: bash

    $ deep diff --help

- Delta

.. code:: bash

    $ deep patch --help

- grep

.. code:: bash

    $ deep grep --help
- extract

.. code:: bash

    $ deep extract --help

Supported data types
~~~~~~~~~~~~~~~~~~~~

int, string, unicode, dictionary, list, tuple, set, frozenset, OrderedDict, NamedTuple, Numpy, custom objects and more!


*****
Pycon
*****

**Pycon 2016 Talk**
A talk was given about the basics of how DeepDiff does what it does at Pycon 2016.
`Diff it to Dig it Pycon 2016 video <https://www.youtube.com/watch?v=J5r99eJIxF4>`_

You can find more information about the contents of that Pycon talk here: http://zepworks.com/blog/diff-it-to-digg-it/



References
==========

.. toctree::
   :maxdepth: 4

   diff
   dsearch
   deephash
   delta
   extract
   commandline
   changelog
   authors
   support


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
