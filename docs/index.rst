.. DeepDiff documentation master file, created by
   sphinx-quickstart on Mon Jul 20 06:06:44 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


DeepDiff 5.0.0 documentation!
=============================

**DeepDiff: Deep Difference of dictionaries, iterables, strings and other objects. It will recursively look for all the changes.**

**DeepSearch: Search for objects within other objects.**

**DeepHash: Hash any object based on their content even if they are not "hashable".**

DeepDiff is tested against Python 3.5, 3.6, 3.7, 3.8 and Pypy3

NOTE: Python 2 is not supported any more. DeepDiff v3.3.0 was the last version to supprt Python 2.

*********
Tutorials
*********

Tutorials can be found on `Zepworks blog <https://zepworks.com/tags/deepdiff/>`_


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
``report_repetition=True`` for getting a report of repetitions.

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


*****
Pycon
*****

**Pycon 2016 Talk**
A talk was given about the basics of how DeepDiff does what it does at Pycon 2016.
`Diff it to Dig it Pycon 2016 video <https://www.youtube.com/watch?v=J5r99eJIxF4>`_

You can find more information about the contents of that Pycon talk here: http://zepworks.com/blog/diff-it-to-digg-it/


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
   changelog
   authors


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
