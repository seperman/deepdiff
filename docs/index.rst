.. DeepDiff documentation master file, created by
   sphinx-quickstart on Mon Jul 20 06:06:44 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


DeepDiff 4.0.5 documentation!
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

DeepDiff prefers to use Murmur3 for hashing. However you have to manually install Murmur3 by running::

    pip install 'deepdiff[murmur]'

Otherwise DeepDiff will be using SHA256 for hashing which is a cryptographic hash and is considerably slower.

If you are running into trouble installing Murmur3, please take a look at the `Troubleshoot <#troubleshoot>`__ section.


Importing
~~~~~~~~~

.. code:: python

    >>> from deepdiff import DeepDiff  # For Deep Difference of 2 objects
    >>> from deepdiff import grep, DeepSearch  # For finding if item exists in an object
    >>> from deepdiff import DeepHash  # For hashing objects based on their contents

********
DeepDiff
********

Read The DeepDiff details in:

:doc:`/diff`

Short introduction

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


Serialization
~~~~~~~~~~~~~

:Serialize to json:

.. code:: python

    >>> t1 = {1: 1, 2: 2, 3: 3}
    >>> t2 = {1: 1, 2: "2", 3: 3}
    >>> ddiff = DeepDiff(t1, t2)
    >>> jsoned = ddiff.to_json()
    >>> jsoned
    '{"type_changes": {"root[2]": {"new_type": "str", "new_value": "2", "old_type": "int", "old_value": 2}}}'


And many more features! Read more in

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

Read the details at:

:doc:`/deephash`

Examples:

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
    {1: 2468916477072481777512283587789292749, 2: -35787773492556653776377555218122431491, ...}

So what is exactly the hash of obj in this case?
DeepHash is calculating the hash of the obj and any other object that obj contains.
The output of DeepHash is a dictionary of object IDs to their hashes.
In order to get the hash of obj itself, you need to use the object (or the id of object) to get its hash:

.. code:: python

    >>> hashes = DeepHash(obj)
    >>> hashes[obj]
    34150898645750099477987229399128149852

Read more in the Deep Hash reference:

:doc:`/deephash`


************
Troubleshoot
************

Murmur3
~~~~~~~

`Failed to build mmh3 when installing DeepDiff`

DeepDiff prefers to use Murmur3 for hashing. However you have to manually install murmur3 by running: `pip install mmh3`

On MacOS Mojave some user experience difficulty when installing Murmur3.

The problem can be solved by running:

    `xcode-select --install`

And then running

    `pip install mmh3`


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

- v4-0-5: Fixing number diffing. Adding number_format_notation and number_to_string_func.
- v4-0-4: Adding ignore_string_case and ignore_type_subclasses
- v4-0-3: Adding versionbump tool for release
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
- v0-5-8: Adding ignore order for unhashables support
- v0-5-7: Adding ignore order support
- v0-5-6: Adding slots support
- v0-5-5: Adding loop detection


Authors
=======

- Sep Dehpour

    - `Github <https://github.com/seperman>`_
    - `ZepWorks <http://www.zepworks.com>`_
    - `Linkedin <http://www.linkedin.com/in/sepehr>`_
    - `Article about Deepdiff <http://zepworks.com/blog/diff-it-to-digg-it/>`_

- Victor Hahn Castell for major contributions

    - `hahncastell.de <http://hahncastell.de>`_
    - `flexoptix.net <http://www.flexoptix.net>`_

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

