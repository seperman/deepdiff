.. DeepDiff documentation master file, created by
   sphinx-quickstart on Mon Jul 20 06:06:44 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


DeepDiff 5.3.0 documentation!
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

DeepDiff is rigorously tested against Python 3.6, 3.7, 3.8, 3.9 and Pypy3

NOTE: Python 2 is not supported any more. DeepDiff v3.3.0 was the last version to supprt Python 2.

***********
What is New
***********

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


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
