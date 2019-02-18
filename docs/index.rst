.. DeepDiff documentation master file, created by
   sphinx-quickstart on Mon Jul 20 06:06:44 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


DeepDiff 4.0.0 documentation!
=============================

**DeepDiff: Deep Difference of dictionaries, iterables, strings and other objects. It will recursively look for all the changes.**

**DeepSearch: Search for objects within other objects.**

**DeepHash: Hash any object based on their content even if they are not "hashable".**

DeepDiff works with Python 3.4, 3.5, 3.6, 3.7, Pypy3

NOTE: Python 2 is not supported any more. DeepDiff v3.3.0 was the last version to supprt Python 2.

************
Installation
************

Install from PyPi::

    pip install deepdiff

Importing
~~~~~~~~~

.. code:: python

    >>> from deepdiff import DeepDiff  # For Deep Difference of 2 objects
    >>> from deepdiff import grep, DeepSearch  # For finding if item exists in an object
    >>> from deepdiff import DeepHash  # For hashing objects based on their contents

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

Text view is the original and currently the default view of DeepDiff.

It is called text view because the results contain texts that represent the path to the data:

Example of using the text view.
    >>> from deepdiff import DeepDiff
    >>> t1 = {1:1, 3:3, 4:4}
    >>> t2 = {1:1, 3:3, 5:5, 6:6}
    >>> ddiff = DeepDiff(t1, t2)
    >>> print(ddiff)
    {'dictionary_item_added': {'root[5]', 'root[6]'}, 'dictionary_item_removed': {'root[4]'}}

So for example ddiff['dictionary_item_removed'] is a set if strings thus this is called the text view.

.. seealso::
    The following examples are using the *default text view.*
    The Tree View is introduced in DeepDiff v3 and provides traversing capabilities through your diffed data and more!
    Read more about the Tree View at :doc:`/diff`

Tree View (new)
---------------

Starting the version v3 You can choose the view into the deepdiff results.
The tree view provides you with tree objects that you can traverse through to find
the parents of the objects that are diffed and the actual objects that are being diffed.
This view is very useful when dealing with nested objects.
Note that tree view always returns results in the form of Python sets.

You can traverse through the tree elements!

.. note::
    The Tree view is just a different representation of the diffed data.
    Behind the scene, DeepDiff creates the tree view first and then converts it to textual representation for the text view.

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

:Example:

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

.. seealso::
    Read more about the Tree View at :doc:`/diff`


Verbose Level
~~~~~~~~~~~~~

Verbose level by default is 1. The possible values are 0, 1 and 2.

-  verbose_level 0: won’t report values when type changed.
-  verbose_level 1: default
-  verbose_level 2: will report values when custom objects or
   dictionaries have items added or removed.

.. seealso::
    Read more about the verbosity at :doc:`/diff`


Serialization
~~~~~~~~~~~~~

DeepDiff uses jsonpickle in order to serialize and deserialize its results into json. This works for both tree view and text view.

:Serialize and then deserialize back to deepdiff:

.. code:: python

    >>> t1 = {1: 1, 2: 2, 3: 3}
    >>> t2 = {1: 1, 2: "2", 3: 3}
    >>> ddiff = DeepDiff(t1, t2)
    >>> jsoned = ddiff.json
    >>> jsoned
    '{"type_changes": {"root[2]": {"py/object": "deepdiff.helper.RemapDict", "new_type": {"py/type": "__builtin__.str"}, "new_value": "2", "old_type": {"py/type": "__builtin__.int"}, "old_value": 2}}}'
    >>> ddiff_new = DeepDiff.from_json(jsoned)
    >>> ddiff == ddiff_new
    True


Read more in

:doc:`/diff`

***********
Deep Search
***********

Deep Search inside objects to find the item matching your criteria.

Note that is searches for either the path to match your criteria or the word in an item.

:Examples:

Importing

.. code:: python

    >>> from deepdiff import DeepSearch, grep
    >>> from pprint import pprint

DeepSearch comes with grep function which is easier to remember!

Search in list for string

.. code:: python

    >>> obj = ["long somewhere", "string", 0, "somewhere great!"]
    >>> item = "somewhere"
    >>> ds = obj | grep(item, verbose_level=2)
    >>> print(ds)
    {'matched_values': {'root[3]': 'somewhere great!', 'root[0]': 'long somewhere'}}

Search in nested data for string

.. code:: python

    >>> obj = ["something somewhere", {"long": "somewhere", "string": 2, 0: 0, "somewhere": "around"}]
    >>> item = "somewhere"
    >>> ds = obj | grep(item, verbose_level=2)
    >>> pprint(ds, indent=2)
    { 'matched_paths': {"root[1]['somewhere']": 'around'},
      'matched_values': { 'root[0]': 'something somewhere',
                          "root[1]['long']": 'somewhere'}}


Read more in the Deep Search references:

:doc:`/dsearch`


*********
Deep Hash
*********
DeepHash calculates the hash of objects based on their contents in a deterministic way.
This way 2 objects with the same content should have the same hash.

The main usage of DeepHash is to calculate the hash of otherwise unhashable objects.
For example you can use DeepHash to calculate the hash of a set or a dictionary!

The core of DeepHash is a deterministic serialization of your object into a string so it
can be passed to a hash function. By default it uses Murmur 3 128 bit hash function.
but you can pass another hash function to it if you want.

Let's say you have a dictionary object.

.. code:: python

    >>> from deepdiff import DeepHash
    >>>
    >>> obj = {1: 2, 'a': 'b'}

If you try to hash it:

.. code:: python

    >>> hash(obj)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: unhashable type: 'dict'

But with DeepHash:

.. code:: python

    >>> from deepdiff import DeepHash
    >>> obj = {1: 2, 'a': 'b'}
    >>> DeepHash(obj)
    {4355639248: (2468916477072481777, 512283587789292749), 4355639280: (-3578777349255665377, -6377555218122431491), 4358636128: (-8839064797231613815, -1822486391929534118), 4358009664: (8833996863197925870, -419376694314494743), 4357467952: (3415089864575009947, 7987229399128149852)}

So what is exactly the hash of obj in this case?
DeepHash is calculating the hash of the obj and any other object that obj contains.
The output of DeepHash is a dictionary of object IDs to their hashes.
In order to get the hash of obj itself, you need to use the object (or the id of object) to get its hash:

.. code:: python

    >>> hashes = DeepHash(obj)
    >>> hashes[obj]
    (3415089864575009947, 7987229399128149852)

Read more in the Deep Hash reference:

:doc:`/deephash`

.. _ignore\_order: #ignore-order
.. _report\_repetition: #report-repetitions
.. _verbose\_level: #verbose-level
.. _exclude\_types\_or\_paths: #exclude-types-or-paths
.. _significant\_digits: #significant-digits
.. _views: #views


References
==========

.. toctree::
   :maxdepth: 2

   diff
   dsearch
   deephash


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Changelog
=========

- v4-0-0: Ending Python 2 support, Adding more functionalities and documentation for DeepHash. Switching to Pytest for testing. Switching to Murmur3 128bit for hashing. Fixing classes which inherit from classes with slots didn't have all of their slots compared. Renaming ContentHash to DeepHash. Adding exclude by path and regex path to DeepHash. Adding ignore_type_number. Adding match_string to DeepSearch. Adding Timedelta object diffing.
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
- v0-5-8: Adding ignore order for unhashables support
- v0-5-7: Adding ignore order support
- v0-5-6: Adding slots support
- v0-5-5: Adding loop detection


Authors
=======

Sep Dehpour

- `Github <https://github.com/seperman>`_
- `ZepWorks <http://www.zepworks.com>`_
- `Linkedin <http://www.linkedin.com/in/sepehr>`_
- `Article about Deepdiff <http://zepworks.com/blog/diff-it-to-digg-it/>`_

Victor Hahn Castell

- `hahncastell.de <http://hahncastell.de>`_
- `flexoptix.net <http://www.flexoptix.net>`_


ALso thanks to:

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

