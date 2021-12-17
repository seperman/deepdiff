:doc:`/index`

Changelog
=========

DeepDiff Changelog

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
