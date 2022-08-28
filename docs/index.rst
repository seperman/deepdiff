.. DeepDiff documentation master file, created by
   sphinx-quickstart on Mon Jul 20 06:06:44 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


DeepDiff 6.1.0 documentation!
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

***********
What is New
***********

DeepDiff 6-1-0
--------------

-  DeepDiff.affected_paths can be used to get the list of all paths
   where a change, addition, or deletion was reported for.
-  DeepDiff.affected_root_keys can be used to get the list of all paths
   where a change, addition, or deletion was reported for.
-  Bugfix: ValueError when using Decimal 0.x #339 by `Enric
   Pou <https://github.com/epou>`__
-  Serialization of UUID

DeepDiff 6-0-0
--------------
-  :ref:`exclude_obj_callback_strict_label`
   parameter is added to DeepDiff by Mikhail Khviyuzov
   `mskhviyu <https://github.com/mskhviyu>`__.
-  A fix for diffing using ``iterable_compare_func`` with nested objects
   by `dtorres-sf <https://github.com/dtorres-sf>`__ who originally
   contributed this feature.
-  Temporarily we are publishing DeepDiff under ``DeepDiff6`` on pypi
   until further notice.

Note: There are no breaking changes in DeepDiff 6 compared to the latest DeepDiff 5 releases.

*********
Tutorials
*********

Tutorials can be found on `Zepworks blog <https://zepworks.com/tags/deepdiff/>`_

************
Installation
************

Install from PyPi::

    pip install deepdiff6

If you want to use DeepDiff from commandline::

    pip install "deepdiff6[cli]"

Read about DeepDiff optimizations at :ref:`optimizations_label`

.. note:: Prior to DeepDiff 6, it was published under DeepDiff name on pypi.

    DeepDiff 6 is being published under DeepDiff6 package name on Pypi temporarily until further notice.


Importing
~~~~~~~~~

.. code:: python

    >>> from deepdiff import DeepDiff  # For Deep Difference of 2 objects
    >>> from deepdiff import grep, DeepSearch  # For finding if item exists in an object
    >>> from deepdiff import DeepHash  # For hashing objects based on their contents
    >>> from deepdiff import Delta  # For creating delta of objects that can be applied later to other objects.
    >>> from deepdiff import extract  # For extracting a path from an object


.. note:: if you want to use DeepDiff via commandline, make sure to run:: 
    pip install "deepdiff6[cli]"

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
   faq
   support


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
