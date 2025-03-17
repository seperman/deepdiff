.. DeepDiff documentation master file, created by
   sphinx-quickstart on Mon Jul 20 06:06:44 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


DeepDiff 8.4.1 documentation!
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

DeepDiff 8-4-0
--------------

    - Adding BaseOperatorPlus base class for custom operators
    - default_timezone can be passed now to set your default timezone to something other than UTC.
    - New summarization algorithm that produces valid json
    - Better type hint support


DeepDiff 8-3-0
--------------

    - Fixed some static typing issues
    - Added the summarize module for better repr of nested values


DeepDiff 8-2-0
--------------

    - Small optimizations so we don't load functions that are not needed
    - Updated the minimum version of Orderly-set 
    - Normalize all datetimes into UTC. Assume timezone naive datetimes are UTC. 


DeepDiff 8-1-0
--------------

    - Removing deprecated lines from setup.py
    - Added ``prefix`` option to ``pretty()``
    - Fixes hashing of numpy boolean values.
    - Fixes **slots** comparison when the attribute doesn’t exist.
    - Relaxing orderly-set reqs
    - Added Python 3.13 support
    - Only lower if clean_key is instance of str
    - Fixes issue where the key deep_distance is not returned when both
      compared items are equal
    - Fixes exclude_paths fails to work in certain cases
    - exclude_paths fails to work
    - Fixes to_json() method chokes on standard json.dumps() kwargs such as
      sort_keys
    - to_dict() method chokes on standard json.dumps() kwargs
    - Fixes accessing the affected_root_keys property on the diff object
      returned by DeepDiff fails when one of the dicts is empty
    - Fixes accessing the affected_root_keys property on the
      diff object returned by DeepDiff fails when one of the dicts is empty
     


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
