:doc:`/index`

Changelog
=========

DeepDiff Changelog

- v8-0-1

    - Bugfix. Numpy should be optional.

- v8-0-0

   - With the introduction of `threshold_to_diff_deeper`, the values returned are different than in previous versions of DeepDiff. You can still get the older values by setting `threshold_to_diff_deeper=0`. However to signify that enough has changed in this release that the users need to update the parameters passed to DeepDiff, we will be doing a major version update.
   - `use_enum_value=True` makes it so when diffing enum, we use the enum's value. It makes it so comparing an enum to a string or any other value is not reported as a type change.
   - `threshold_to_diff_deeper=float` is a number between 0 and 1. When comparing dictionaries that have a small intersection of keys, we will report the dictionary as a `new_value` instead of reporting individual keys changed. If you set it to zero, you get the same results as DeepDiff 7.0.1 and earlier, which means this feature is disabled. The new default is 0.33 which means if less that one third of keys between dictionaries intersect, report it as a new object.
   - Deprecated `ordered-set` and switched to `orderly-set`. The `ordered-set` package was not being maintained anymore and starting Python 3.6, there were better options for sets that ordered. I forked one of the new implementations, modified it, and published it as `orderly-set`.
   - Added `use_log_scale:bool` and `log_scale_similarity_threshold:float`. They can be used to ignore small changes in numbers by comparing their differences in logarithmic space. This is different than ignoring the difference based on significant digits.
   - json serialization of reversed lists.
   - Fix for iterable moved items when `iterable_compare_func` is used.
   - Pandas and Polars support 

-  v7-0-1

   - Fixes the translation between Difflib opcodes and Delta flat rows.

-  v7-0-0

   -  When verbose=2, return ``new_path`` when the ``path`` and
      ``new_path`` are different (for example when ignore_order=True and
      the index of items have changed).
   -  Dropping support for Python 3.7
   -  Introducing serialize to flat rows for delta objects.
   -  fixes the issue with hashing ``datetime.date`` objects where it
      treated them as numbers instead of dates (fixes #445).
   -  upgrading orjson to the latest version
   -  Fix for bug when diffing two lists with ignore_order and providing
      compare_func
   -  Fixes “Wrong diff on list of strings” #438
   -  Supporting Python 3.12 in the build process by `Leo
      Sin <https://github.com/leoslf>`__
   -  Fixes “Instantiating a Delta with a flat_dict_list unexpectedly
      mutates the flat_dict_list” #457 by
      `sf-tcalhoun <https://github.com/sf-tcalhoun>`__
   -  Fixes “Error on Delta With None Key and Removed Item from List”
      #441
   -  Fixes “Error when comparing two nested dicts with 2 added fields”
      #450
   -  Fixes “Error when subtracting Delta from a dictionary” #443

-  v6-7-1

   -  Support for subtracting delta objects when iterable_compare_func
      is used.
   -  Better handling of force adding a delta to an object.
   -  Fix for
      ```Can't compare dicts with both single and double quotes in keys`` <https://github.com/seperman/deepdiff/issues/430>`__
   -  Updated docs for Inconsistent Behavior with math_epsilon and
      ignore_order = True

-  v6-7-0

   -  Delta can be subtracted from other objects now.
   -  verify_symmetry is deprecated. Use bidirectional instead.
   -  always_include_values flag in Delta can be enabled to include
      values in the delta for every change.
   -  Fix for Delta.\__add\_\_ breaks with esoteric dict keys.

-  v6-6-1

    -  Fix for `DeepDiff raises decimal exception when using significant
       digits <https://github.com/seperman/deepdiff/issues/426>`__
    -  Introducing group_by_sort_key
    -  Adding group_by 2D. For example
       ``group_by=['last_name', 'zip_code']``

-  v6-6-0

   -  Numpy 2.0 support
   -  Adding
      `Delta.to_flat_dicts <https://zepworks.com/deepdiff/current/serialization.html#delta-serialize-to-flat-dictionaries>`__

-  v6-5-0

   -  Adding
      ```parse_path`` <https://github.com/seperman/deepdiff/pull/419>`__

-  v6-4-1

   -  Bugfix: Keep Numpy Optional

-  v6-4-0

   -  `Add Ignore List Order Option to
      DeepHash <https://github.com/seperman/deepdiff/pull/403>`__ by
      `Bobby Morck <https://github.com/bmorck>`__
   -  `pyyaml to 6.0.1 to fix cython build
      problems <https://github.com/seperman/deepdiff/pull/406>`__ by
      `Robert Bo Davis <https://github.com/robert-bo-davis>`__
   -  `Precompiled regex simple
      diff <https://github.com/seperman/deepdiff/pull/413>`__ by
      `cohml <https://github.com/cohml>`__
   -  New flag: ``zip_ordered_iterables`` for forcing iterable items to
      be compared one by one.

-  v6-3-1

   -  Bugfix deephash for paths by
      `maggelus <https://github.com/maggelus>`__
   -  Bugfix deephash compiled regex
      `maggelus <https://github.com/maggelus>`__
   -  Fix tests dependent on toml by
      `martin-kokos <https://github.com/martin-kokos>`__
   -  Bugfix for ``include_paths`` for nested dictionaries by
      `kor4ik <https://github.com/kor4ik>`__
   -  Use tomli and tomli-w for dealing with tomli files by
      `martin-kokos <https://github.com/martin-kokos>`__
   -  Bugfix for ``datetime.date`` by `Alex
      Sauer-Budge <https://github.com/amsb>`__

-  v6-3-0

   -  ``PrefixOrSuffixOperator``: This operator will skip strings that
      are suffix or prefix of each other.
   -  ``include_obj_callback`` and ``include_obj_callback_strict`` are
      added by `Håvard Thom <https://github.com/havardthom>`__.
   -  Fixed a corner case where numpy’s ``np.float32`` nans are not
      ignored when using ``ignore_nan_equality`` by `Noam
      Gottlieb <https://github.com/noamgot>`__
   -  ``orjson`` becomes optional again.
   -  Fix for ``ignore_type_in_groups`` with numeric values so it does
      not report number changes when the number types are different.

-  v6-2-3

   -  Switching to Orjson for serialization to improve the performance.
   -  Setting ``equal_nan=ignore_nan_inequality`` in the call for
      ``np.array_equal``
   -  Using Pytest’s tmp_path fixture instead of ``/tmp/``

-  v6-2-2

   -  Enum test fix for python 3.11
   -  Adding support for dateutils rrules

-  v6-2-1

   -  Removed the print statements.

-  v6-2-0

   -  Major improvement in the diff report for lists when items are all
      hashable and the order of items is important.

-  v6-1-0

   -  DeepDiff.affected_paths can be used to get the list of all paths
      where a change, addition, or deletion was reported for.
   -  DeepDiff.affected_root_keys can be used to get the list of all
      paths where a change, addition, or deletion was reported for.
   -  Bugfix: ValueError when using Decimal 0.x #339 by `Enric
      Pou <https://github.com/epou>`__
   -  Serialization of UUID

-  v6-0-0

   -  `Exclude obj callback
      strict <https://github.com/seperman/deepdiff/pull/320/files>`__
      parameter is added to DeepDiff by Mikhail Khviyuzov
      `mskhviyu <https://github.com/mskhviyu>`__.
   -  A fix for diffing using ``iterable_compare_func`` with nested
      objects by `dtorres-sf <https://github.com/dtorres-sf>`__ who
      originally contributed this feature.
-  v5-7-0:

   -  https://github.com/seperman/deepdiff/pull/284 Bug-Fix: TypeError
      in \_get_numbers_distance() when ignore_order = True by
      @Dhanvantari
   -  https://github.com/seperman/deepdiff/pull/280 Add support for
      UUIDs by @havardthom
   -  Major bug in delta when it comes to iterable items added or
      removed is investigated by @uwefladrich and resolved by @seperman
- v5-6-0: Adding custom operators, and ignore_order_func. Bugfix: verbose_level==0 should disable values_changes. Bugfix: unprocessed key error.
- v5-5-0: adding iterable_compare_func for DeepDiff, adding output_format of list for path() in tree view.
- v5-4-0: adding strict_checking for numbers in DeepSearch.
- v5-3-0: add support for regular expressions in DeepSearch.
- v5-2-3: Retaining the order of multiple dictionary items added via Delta. Fixed the typo with yml files in deep cli. Fixing Grep RecursionError where using non UTF-8 character. Allowing kwargs to be passed to to_json method.
- v5-2-2: Fixed Delta serialization when None type is present.
- v5-2-0: Removed Murmur3 as the preferred hashing method. Using SHA256 by default now. Added commandline for deepdiff. Added group_by. Added math_epsilon. Improved ignoring of NoneType.
- v5-0-2: Bug Fix NoneType in ignore type groups https://github.com/seperman/deepdiff/issues/207
- v5-0-1: Bug fix to not apply format to non numbers.
- v5-0-0: Introducing the Delta object, Improving Numpy support, Fixing tuples comparison when ignore_order=True, Dramatically improving the results when ignore_order=True by running in passes, Introducing pretty print view, deep_distance, purge, progress logging, cache and truncate_datetime.
- v4-3-3: Adds support for datetime.time
- v4-3-2: Deprecation Warning Enhancement
- v4-3-1: Fixing the issue with exclude_path and hash calculations when dictionaries were inside iterables. https://github.com/seperman/deepdiff/issues/174
- v4-3-0: adding exclude_obj_callback
- v4-2-0: .json property is finally removed. Fix for Py3.10. Dropping support for EOL Python 3.4. Ignoring private keys when calculating hashes. For example __init__ is not a part of hash calculation anymore. Fix for #166 Problem with comparing lists, with an boolean as element.
- v4-1-0: .json property is finally removed.
- v4-0-9: Fixing the bug for hashing custom unhashable objects
- v4-0-8: Adding ignore_nan_inequality for float('nan')
- v4-0-7: Hashing of the number 1 vs. True
- v4-0-6: found a tiny bug in Python formatting of numbers in scientific notation. Added a workaround.
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


Back to :doc:`/index`
