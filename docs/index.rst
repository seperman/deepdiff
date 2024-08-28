.. DeepDiff documentation master file, created by
   sphinx-quickstart on Mon Jul 20 06:06:44 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


DeepDiff 8.0.1 documentation!
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
What Is New
***********

DeepDiff 8-0-1

    - Bugfix. Numpy should be optional.

DeepDiff 8-0-0
--------------

    - With the introduction of `threshold_to_diff_deeper`, the values returned are different than in previous versions of DeepDiff. You can still get the older values by setting `threshold_to_diff_deeper=0`. However to signify that enough has changed in this release that the users need to update the parameters passed to DeepDiff, we will be doing a major version update.
    - `use_enum_value=True` makes it so when diffing enum, we use the enum's value. It makes it so comparing an enum to a string or any other value is not reported as a type change.
    - `threshold_to_diff_deeper=float` is a number between 0 and 1. When comparing dictionaries that have a small intersection of keys, we will report the dictionary as a `new_value` instead of reporting individual keys changed. If you set it to zero, you get the same results as DeepDiff 7.0.1 and earlier, which means this feature is disabled. The new default is 0.33 which means if less that one third of keys between dictionaries intersect, report it as a new object.
    - Deprecated `ordered-set` and switched to `orderly-set`. The `ordered-set` package was not being maintained anymore and starting Python 3.6, there were better options for sets that ordered. I forked one of the new implementations, modified it, and published it as `orderly-set`.
    - Added `use_log_scale:bool` and `log_scale_similarity_threshold:float`. They can be used to ignore small changes in numbers by comparing their differences in logarithmic space. This is different than ignoring the difference based on significant digits.
    - json serialization of reversed lists.
    - Fix for iterable moved items when `iterable_compare_func` is used.
    - Pandas and Polars support 


DeepDiff 7-0-0
--------------

    -  DeepDiff 7 comes with an improved delta object. `Delta to flat
       dictionaries <https://zepworks.com/deepdiff/current/serialization.html#delta-serialize-to-flat-dictionaries>`__
       have undergone a major change. We have also introduced `Delta
       serialize to flat
       rows <https://zepworks.com/deepdiff/current/serialization.html#delta-serialize-to-flat-rows>`__.
    -  Subtracting delta objects have dramatically improved at the cost of
       holding more metadata about the original objects.
    -  When ``verbose=2``, and the “path” of an item has changed in a report
       between t1 and t2, we include it as ``new_path``.
    -  ``path(use_t2=True)`` returns the correct path to t2 in any reported
       change in the `tree view <https://zepworks.com/deepdiff/current/view.html#tree-view>`__
    -  Python 3.7 support is dropped and Python 3.12 is officially
       supported.


DeepDiff 6-7-1
--------------

   -  Support for subtracting delta objects when iterable_compare_func
      is used.
   -  Better handling of force adding a delta to an object.
   -  Fix for
      `Can't compare dicts with both single and double quotes in keys <https://github.com/seperman/deepdiff/issues/430>`__
   -  Updated docs for Inconsistent Behavior with math_epsilon and
      ignore_order = True

DeepDiff 6-7-0
--------------

    -  Delta can be subtracted from other objects now.
    -  verify_symmetry is deprecated. Use bidirectional instead.
    -  :ref:`always_include_values_label` flag in Delta can be enabled to include
       values in the delta for every change.
    -  Fix for Delta.\__add\_\_ breaks with esoteric dict keys.
    -  :ref:`delta_from_flat_dicts_label` can be used to load a delta from the list of flat dictionaries.


DeepDiff 6-6-1
--------------

    -  Fix for `DeepDiff raises decimal exception when using significant
       digits <https://github.com/seperman/deepdiff/issues/426>`__
    -  Introducing group_by_sort_key
    -  Adding group_by 2D. For example
       ``group_by=['last_name', 'zip_code']``

DeepDiff 6-6-0
--------------
    
    - :ref:`delta_to_flat_dicts_label` can be used to serialize delta objects into a flat list of dictionaries.
    - `NumPy 2.0 compatibility <https://github.com/seperman/deepdiff/pull/422>`__ by `William Jamieson <https://github.com/WilliamJamieson>`__


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
