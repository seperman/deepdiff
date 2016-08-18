.. DeepDiff documentation master file, created by
   sphinx-quickstart on Mon Jul 20 06:06:44 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

DeepDiff 2.5.1 documentation!
=============================

**DeepDiff: Deep Difference of dictionaries, iterables and almost any other object recursively.**

DeepDiff works with Python 2.7, 3.3, 3.4, 3.5, Pypy, Pypy3

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

In addition to the 2 objects being compared:

-  `ignore\_order`_
-  `report\_repetition`_
-  `verbose\_level`_

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

Verbose Level
-------------

Verbose level by default is 1. The possible values are 0, 1 and 2.

-  Verbose level 0: won’t report values when type changed.
-  Verbose level 1: default
-  Verbose level 2: will report values when custom objects or
   dictionaries have items added or removed.


.. _ignore\_order: #ignore-order
.. _report\_repetition: #report-repetitions
.. _verbose\_level: #verbose-level


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
