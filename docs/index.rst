.. DeepDiff documentation master file, created by
   sphinx-quickstart on Mon Jul 20 06:06:44 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to DeepDiff's documentation!
====================================

**DeepDiff: Deep Difference of dictionaries, iterables and almost any other object recursively.**

DeepDiff works with Python 2.7, 3.3, 3.4, 3.5, Pypy, Pypy3

************
Installation
************

Install from PyPi::

    pip install deepdiff


**************
DeepDiff 2.0.0
**************

.. toctree::
   :maxdepth: 2

.. automodule:: deepdiff

.. autoclass:: DeepDiff
    :members:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Changelog
=========

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


Author
======

Sep Dehpour

- `Github <https://github.com/seperman>`_
- `ZepWorks <http://www.zepworks.com>`_
- `Linkedin <http://www.linkedin.com/in/sepehr>`_
- `Article about Deepdiff <http://zepworks.com/blog/diff-it-to-digg-it/>`_

Thanks to:

- nfvs for Travis-CI setup script
- brbsix for initial Py3 porting
- WangFenjin for unicode support
- timoilya for comparing list of sets when ignoring order
- Bernhard10 for significant digits comparison
- b-jazz for PEP257 cleanup, Standardize on full names, fixing line endings.
- Victor Hahn Castell @ Flexoptix for deep set comparison
