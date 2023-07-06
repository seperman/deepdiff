.. DeepDiff documentation master file, created by
   sphinx-quickstart on Mon Jul 20 06:06:44 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


DeepDiff 6.3.1 documentation!
=============================

*******
Modules
*******

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


DeepDiff 6-3-1
--------------

This release includes many bug fixes.

-  Bugfix deephash for paths by `maggelus <https://github.com/maggelus>`__
-  Bugfix deephash compiled regex `maggelus <https://github.com/maggelus>`__
-  Fix tests dependent on toml by `martin-kokos <https://github.com/martin-kokos>`__
-  Bugfix for ``include_paths`` for nested dictionaries by `kor4ik <https://github.com/kor4ik>`__
-  Use tomli and tomli-w for dealing with tomli files by `martin-kokos <https://github.com/martin-kokos>`__
-  Bugfix for ``datetime.date`` by `Alex Sauer-Budge <https://github.com/amsb>`__


DeepDiff 6-3-0
--------------

-  :ref:`prefix_or_suffix_operator_label`: This operator will skip strings that are
   suffix or prefix of each other.
-  :ref:`include_obj_callback_label` and :ref:`include_obj_callback_strict_label` are
   added by `Håvard Thom <https://github.com/havardthom>`__.
-  Fixed a corner case where numpy’s ``np.float32`` nans are not ignored
   when using ``ignore_nan_equality`` by `Noam
   Gottlieb <https://github.com/noamgot>`__
-  ``orjson`` becomes optional again.
-  Fix for ``ignore_type_in_groups`` with numeric values so it does not report number changes when the number types are different.

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

If you want to improve the performance of DeepDiff with certain processes such as json serialization::

    pip install "deepdiff[optimize]"

Read about DeepDiff optimizations at :ref:`optimizations_label`

Importing
~~~~~~~~~

.. code:: python

    >>> from deepdiff import DeepDiff  # For Deep Difference of 2 objects
    >>> from deepdiff import grep, DeepSearch  # For finding if item exists in an object
    >>> from deepdiff import DeepHash  # For hashing objects based on their contents
    >>> from deepdiff import Delta  # For creating delta of objects that can be applied later to other objects.
    >>> from deepdiff import extract  # For extracting a path from an object


.. note:: if you want to use DeepDiff via commandline, make sure to run:: 
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
