.. DeepDiff documentation master file, created by
   sphinx-quickstart on Mon Jul 20 06:06:44 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


DeepDiff 5.6.0 documentation!
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

DeepDiff is rigorously tested against Python 3.6 up to 3.10 and Pypy3

NOTE: Python 2 is not supported any more. DeepDiff v3.3.0 was the last version to supprt Python 2.

***********
What is New
***********

New In DeepDiff 5-6-0
---------------------

**Create custom operators!**

    >>> from deepdiff import DeepDiff
    >>> from deepdiff.operator import BaseOperator
    >>> class CustomClass:
    ...     def __init__(self, d: dict, l: list):
    ...         self.dict = d
    ...         self.dict['list'] = l
    ...
    >>>
    >>> custom1 = CustomClass(d=dict(a=1, b=2), l=[1, 2, 3])
    >>> custom2 = CustomClass(d=dict(c=3, d=4), l=[1, 2, 3, 2])
    >>> custom3 = CustomClass(d=dict(a=1, b=2), l=[1, 2, 3, 4])
    >>>
    >>>
    >>> class ListMatchOperator(BaseOperator):
    ...     def give_up_diffing(self, level, diff_instance):
    ...         if set(level.t1.dict['list']) == set(level.t2.dict['list']):
    ...             return True
    ...
    >>>
    >>> DeepDiff(custom1, custom2, custom_operators=[
    ...     ListMatchOperator(types=[CustomClass])
    ... ])
    {}
    >>>
    >>>
    >>> DeepDiff(custom2, custom3, custom_operators=[
    ...     ListMatchOperator(types=[CustomClass])
    ... ])
    {'dictionary_item_added': [root.dict['a'], root.dict['b']], 'dictionary_item_removed': [root.dict['c'], root.dict['d']], 'values_changed': {"root.dict['list'][3]": {'new_value': 4, 'old_value': 2}}}
    >>>


**Dynamic ignore order function**

Ignoring order when certain word in the path

    >>> from deepdiff import DeepDiff
    >>> t1 = {'a': [1, 2], 'b': [3, 4]}
    >>> t2 = {'a': [2, 1], 'b': [4, 3]}
    >>> DeepDiff(t1, t2, ignore_order=True)
    {}
    >>> def ignore_order_func(level):
    ...     return 'a' in level.path()
    ...
    >>> DeepDiff(t1, t2, ignore_order=True, ignore_order_func=ignore_order_func)
    {'values_changed': {"root['b'][0]": {'new_value': 4, 'old_value': 3}, "root['b'][1]": {'new_value': 3, 'old_value': 4}}}


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
   faq
   support


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
