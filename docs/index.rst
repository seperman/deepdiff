.. DeepDiff documentation master file, created by
   sphinx-quickstart on Mon Jul 20 06:06:44 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

DeepDiff 3.0.0 documentation!
=============================

**DeepDiff: Deep Difference of dictionaries, iterables and almost any other object recursively.**

DeepDiff works with Python 2.7, 3.3, 3.4, 3.5, 3.6, Pypy, Pypy3

************
Installation
************

Install from PyPi::

    pip install deepdiff

Importing
~~~~~~~~~

.. code:: python

    >>> from deepdiff import DeepDiff  # For Deep Difference of 2 objects
    >>> from deepdiff import DeepSearch  # For finding if item exists in an object

********
Features
********

Parameters
~~~~~~~~~~

-  t1 (the first object)
-  t2 (the second object)
-  `ignore\_order`_
-  `report\_repetition`_
-  `exclude\_types\_or\_paths`_
-  `significant\_digits`_
-  `views`_

Supported data types
~~~~~~~~~~~~~~~~~~~~

int, string, dictionary, list, tuple, set, frozenset, OrderedDict,
NamedTuple and custom objects!

Ignore Order
~~~~~~~~~~~~

Sometimes you don’t care about the order of objects when comparing them.
In those cases, you can set ``ignore_order=True``. However this flag
won’t report the repetitions to you. You need to additionally enable
``report_report_repetition=True`` for getting a report of repetitions.

List difference ignoring order or duplicates
--------------------------------------------

.. code:: python

    >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
    >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 3, 2, 3]}}
    >>> ddiff = DeepDiff(t1, t2, ignore_order=True)
    >>> print (ddiff)
    {}

Report repetitions
~~~~~~~~~~~~~~~~~~

This flag ONLY works when ignoring order is enabled.

.. code:: python

    t1 = [1, 3, 1, 4]
    t2 = [4, 4, 1]
    ddiff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True)
    print(ddiff)

which will print you:

.. code:: python

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

Exclude types or paths
~~~~~~~~~~~~~~~~~~~~~~

Exclude certain types from comparison
-------------------------------------

.. code:: python

    >>> l1 = logging.getLogger("test")
    >>> l2 = logging.getLogger("test2")
    >>> t1 = {"log": l1, 2: 1337}
    >>> t2 = {"log": l2, 2: 1337}
    >>> print(DeepDiff(t1, t2, exclude_types={logging.Logger}))
    {}

Exclude part of your object tree from comparison
------------------------------------------------

.. code:: python

    >>> t1 = {"for life": "vegan", "ingredients": ["no meat", "no eggs", "no dairy"]}
    >>> t2 = {"for life": "vegan", "ingredients": ["veggies", "tofu", "soy sauce"]}
    >>> print (DeepDiff(t1, t2, exclude_paths={"root['ingredients']"}))
    {}

Significant Digits
~~~~~~~~~~~~~~~~~~

Digits **after** the decimal point. Internally it uses
“{:.Xf}”.format(Your Number) to compare numbers where
X=significant\_digits

.. code:: python

    >>> t1 = Decimal('1.52')
    >>> t2 = Decimal('1.57')
    >>> DeepDiff(t1, t2, significant_digits=0)
    {}
    >>> DeepDiff(t1, t2, significant_digits=1)
    {'values_changed': {'root': {'old_value': Decimal('1.52'), 'new_value': Decimal('1.57')}}}

Approximate float comparison:
-----------------------------

.. code:: python

    >>> t1 = [ 1.1129, 1.3359 ]
    >>> t2 = [ 1.113, 1.3362 ]
    >>> pprint(DeepDiff(t1, t2, significant_digits=3))
    {}
    >>> pprint(DeepDiff(t1, t2))
    {'values_changed': {'root[0]': {'new_value': 1.113, 'old_value': 1.1129},
                        'root[1]': {'new_value': 1.3362, 'old_value': 1.3359}}}
    >>> pprint(DeepDiff(1.23*10**20, 1.24*10**20, significant_digits=1))
    {'values_changed': {'root': {'new_value': 1.24e+20, 'old_value': 1.23e+20}}}


Views
~~~~~

Text View (default)
-------------------

Text view is the default view. All the examples above are using the text view.

Tree View (new)
---------------

The tree view provides you with tree objects that you can traverse through to find
the parents of the objects that are diffed and the actual objects that are being diffed.
This view is very useful when dealing with nested objects.
Note that tree view always returns results in the form of Python sets.

You can traverse through the tree elements by using up, down, t1, t2

.. code:: text

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

The tree view allows you to have more than mere textual representaion of the diffed objects.
It gives you the actual objects (t1, t2) throughout the tree of parents and children.
We will see through examples how this affects how you retrieve the individual results:

Value of an item has changed (Tree View)

.. code:: python

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

List difference (Tree View)

.. code:: python

    >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3, 4]}}
    >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2]}}
    >>> ddiff = DeepDiff(t1, t2, view='tree')
    >>> ddiff
    {'iterable_item_removed': {<root[4]['b'][3] t1:4, t2:None>, <root[4]['b'][2] t1:3, t2:None>}}
    >>> # Note that the iterable_item_removed is a set. In this case it has 2 items in it.
    >>> # One way to get one item from the set is to convert it to a list
    >>> # And then get the first item of the list:
    >>> removed = list(ddiff['iterable_item_removed'])[0]
    >>> removed
    <root[4]['b'][2] t1:3, t2:None>
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


List difference 2  (Tree View)

.. code:: python

    >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
    >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 3, 2, 3]}}
    >>> ddiff = DeepDiff(t1, t2, view='tree')
    >>> pprint(ddiff, indent = 2)
    { 'iterable_item_added': {<root[4]['b'][3] t1:None, t2:3>},
      'values_changed': { <root[4]['b'][1] t1:2, t2:3>,
                          <root[4]['b'][2] t1:3, t2:2>}}
    >>>
    >>> # Note that iterable_item_added is a set with one item.
    >>> # So in order to get that one item from it, we can do:
    >>> (added,) = ddiff['iterable_item_added']
    >>> added
    <root[4]['b'][3] t1:None, t2:3>
    >>> added.up.up
    <root[4] t1:{'a': 'hello...}, t2:{'a': 'hello...}>
    >>> added.up.up.path()
    'root[4]'
    >>> added.up.up.down
    <root[4]['b'] t1:[1, 2, 3], t2:[1, 3, 2, 3]>
    # going up twice and then down twice gives you the same node in the tree:
    >>> added.up.up.down.down == added
    True


List difference ignoring order but reporting repetitions (Tree View)

.. code:: python

    >>> t1 = [1, 3, 1, 4]
    >>> t2 = [4, 4, 1]
    >>> ddiff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True, view='tree')
    >>> pprint(ddiff, indent=2)
    { 'iterable_item_removed': {<root[1] t1:3, t2:None>},
      'repetition_change': { <root[3] {'repetition': {'old_repeat': 1,...}>,
                             <root[0] {'repetition': {'old_repeat': 2,...}>}}
    >>>
    >>> # repetition_change is a set with 2 items.
    >>> # in order to get those 2 items, we can do the following.
    >>> # or we can convert the set to list and get the list items.
    >>> # or we can iterate through the set items
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


Verbose Level
~~~~~~~~~~~~~

Verbose level by default is 1. The possible values are 0, 1 and 2.

-  Verbose level 0: won’t report values when type changed.
-  Verbose level 1: default
-  Verbose level 2: will report values when custom objects or
   dictionaries have items added or removed.


.. _ignore\_order: #ignore-order
.. _report\_repetition: #report-repetitions
.. _verbose\_level: #verbose-level
.. _exclude\_types\_or\_paths: #exclude-types-or-paths
.. _significant\_digits: #significant-digits
.. _views: #views

DeepDiff Reference
==================

:doc:`/diff`


DeepSearch Reference
====================

:doc:`/dsearch`


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Changelog
=========

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
- v0-5-8: Adding ignore order for unhashables support
- v0-5-7: Adding ignore order support
- v0-5-6: Adding slots support
- v0-5-5: Adding loop detection


Author
======

Sep Dehpour

- `Github <https://github.com/seperman>`_
- `ZepWorks <http://www.zepworks.com>`_
- `Linkedin <http://www.linkedin.com/in/sepehr>`_
- `Article about Deepdiff <http://zepworks.com/blog/diff-it-to-digg-it/>`_

Thanks to:

- nfvs for Travis-CI setup script
- brbsix for initial Py3 porting
- WangFenjin for unicode support
- timoilya for comparing list of sets when ignoring order
- Bernhard10 for significant digits comparison
- b-jazz for PEP257 cleanup, Standardize on full names, fixing line endings.
- Victor Hahn Castell @ Flexoptix for deep set comparison
