.. DeepDiff documentation master file, created by
   sphinx-quickstart on Mon Jul 20 06:06:44 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


DeepDiff 5.0.2 documentation!
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

*************************
Supported Python Versions
*************************

DeepDiff is rigorously tested against Python 3.5, 3.6, 3.7, 3.8 and Pypy3

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

DeepDiff prefers to use Murmur3 for hashing. However you need to manually install Murmur3 by running::

    pip install 'deepdiff[murmur]'

Otherwise DeepDiff will be using SHA256 for hashing which is a cryptographic hash and is considerably slower for hashing.
However hashing is not usually the bottleneck when dealing with big objects. Read more about DeepDiff :ref:`optimizations_label`

If you are running into trouble installing Murmur3, please take a look at the :ref:`troubleshoot_label` section.


Importing
~~~~~~~~~

.. code:: python

    >>> from deepdiff import DeepDiff  # For Deep Difference of 2 objects
    >>> from deepdiff import grep, DeepSearch  # For finding if item exists in an object
    >>> from deepdiff import DeepHash  # For hashing objects based on their contents
    >>> from deepdiff import Delta  # For creating delta of objects that can be applied later to other objects.
    >>> from deepdiff import extract  # For extracting a path from an object


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
   changelog
   authors


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
