#!/usr/bin/env python

# In order to run the docstrings:
# python3 -m deepdiff.diff
# You might need to run it many times since dictionaries come in different orders
# every time you run the docstrings.
# However the docstring expects it in a specific order in order to pass!
import difflib
import logging
from copy import deepcopy
from collections.abc import Mapping, Iterable
from collections import defaultdict
from decimal import Decimal
from itertools import zip_longest
from ordered_set import OrderedSet
from deepdiff.helper import (strings, bytes_type, numbers, ListItemRemovedOrAdded, notpresent,
                             IndexedHash, unprocessed, add_to_frozen_set,
                             convert_item_or_items_into_set_else_none, get_type,
                             convert_item_or_items_into_compiled_regexes_else_none,
                             type_is_subclass_of_type_group, type_in_type_group, get_doc,
                             number_to_string, KEY_TO_VAL_STR, booleans,
                             np_ndarray, get_numpy_ndarray_rows, OrderedSetPlus, RepeatedTimer,
                             skipped, get_numeric_types_distance, TEXT_VIEW, TREE_VIEW, DELTA_VIEW,
                             not_found, np)
from deepdiff.serialization import SerializationMixin
from deepdiff.distance import DistanceMixin
from deepdiff.model import (
    RemapDict, ResultDict, TextResult, TreeResult, DiffLevel,
    DictRelationship, AttributeRelationship,
    SubscriptableIterableRelationship, NonSubscriptableIterableRelationship,
    SetRelationship, NumpyArrayRelationship)
from deepdiff.deephash import DeepHash, combine_hashes_lists, default_hasher
from deepdiff.base import Base

logger = logging.getLogger(__name__)


MAX_PASSES_REACHED_MSG = (
    'DeepDiff has reached the max number of passes of {}. '
    'You can possibly get more accurate results by increasing the max_passes parameter.')

MAX_DIFFS_REACHED_MSG = (
    'DeepDiff has reached the max number of diffs of {}. '
    'You can possibly get more accurate results by increasing the max_diffs parameter.')


notpresent_indexed = IndexedHash(indexes=[0], item=notpresent)

doc = get_doc('diff_doc.rst')


PROGRESS_MSG = "DeepDiff in progress. Pass #{}, Diff #{}"


def _report_progress(_stats, progress_logger):
    progress_logger(PROGRESS_MSG.format(_stats[PASSES_COUNT], _stats[DIFF_COUNT]))


CACHE_LEVEL_HIT = 'CACHE LEVEL HIT'
DISTANCE_CACHE_HIT = 'DISTANCE CACHE HIT'
DIFF_COUNT = 'DIFF COUNT'
PASSES_COUNT = 'PASSES COUNT'
MAX_PASS_LIMIT_REACHED = 'MAX PASS LIMIT REACHED'
MAX_DIFF_LIMIT_REACHED = 'MAX DIFF LIMIT REACHED'

# What is the threshold to consider 2 items to be pairs. Only used when ignore_order = True.
CUTOFF_DISTANCE_FOR_PAIRS_DEFAULT = Decimal('0.3')


class DeepDiff(ResultDict, SerializationMixin, DistanceMixin, Base):
    __doc__ = doc

    # Maximum number of calculated distances between pairs to be tracked.
    # For huge lists, this number may need to be modified at the cost of more memory usage.
    # Only used when ignore_order = True.
    MAX_COMMON_PAIR_DISTANCES = 10000

    def __init__(self,
                 t1,
                 t2,
                 ignore_order=False,
                 report_repetition=False,
                 significant_digits=None,
                 number_format_notation="f",
                 exclude_paths=None,
                 exclude_regex_paths=None,
                 exclude_types=None,
                 ignore_type_in_groups=None,
                 ignore_string_type_changes=False,
                 ignore_numeric_type_changes=False,
                 ignore_type_subclasses=False,
                 ignore_string_case=False,
                 exclude_obj_callback=None,
                 number_to_string_func=None,
                 ignore_nan_inequality=False,
                 ignore_private_variables=True,
                 verbose_level=1,
                 view=TEXT_VIEW,
                 hasher=None,
                 hashes=None,
                 parameters=None,
                 max_passes=10000000,
                 max_diffs=None,
                 cutoff_distance_for_pairs=CUTOFF_DISTANCE_FOR_PAIRS_DEFAULT,
                 log_frequency_in_sec=0,
                 progress_logger=logger.warning,
                 _stats=None,
                 _cache=None,
                 **kwargs):
        if kwargs:
            raise ValueError((
                "The following parameter(s) are not valid: %s\n"
                "The valid parameters are ignore_order, report_repetition, significant_digits, "
                "number_format_notation, exclude_paths, exclude_types, exclude_regex_paths, ignore_type_in_groups, "
                "ignore_string_type_changes, ignore_numeric_type_changes, ignore_type_subclasses, ignore_private_variables, "
                "ignore_nan_inequality, number_to_string_func, verbose_level, "
                "view, hasher, hashes, max_passes, max_diffs, cutoff_distance_for_pairs, "
                "log_frequency_in_sec, _stats, and parameters.") % ', '.join(kwargs.keys()))

        if parameters:
            self.__dict__ = deepcopy(parameters)
        else:
            self.ignore_order = ignore_order
            ignore_type_in_groups = ignore_type_in_groups or []
            if numbers == ignore_type_in_groups or numbers in ignore_type_in_groups:
                ignore_numeric_type_changes = True
            self.ignore_numeric_type_changes = ignore_numeric_type_changes
            if strings == ignore_type_in_groups or strings in ignore_type_in_groups:
                ignore_string_type_changes = True
            self.ignore_string_type_changes = ignore_string_type_changes
            self.ignore_type_in_groups = self.get_ignore_types_in_groups(
                ignore_type_in_groups=ignore_type_in_groups,
                ignore_string_type_changes=ignore_string_type_changes,
                ignore_numeric_type_changes=ignore_numeric_type_changes,
                ignore_type_subclasses=ignore_type_subclasses)
            self.report_repetition = report_repetition
            self.exclude_paths = convert_item_or_items_into_set_else_none(exclude_paths)
            self.exclude_regex_paths = convert_item_or_items_into_compiled_regexes_else_none(exclude_regex_paths)
            self.exclude_types = set(exclude_types) if exclude_types else None
            self.exclude_types_tuple = tuple(exclude_types) if exclude_types else None  # we need tuple for checking isinstance
            self.ignore_type_subclasses = ignore_type_subclasses
            self.type_check_func = type_is_subclass_of_type_group if ignore_type_subclasses else type_in_type_group
            self.ignore_string_case = ignore_string_case
            self.exclude_obj_callback = exclude_obj_callback
            self.number_to_string = number_to_string_func or number_to_string
            self.ignore_private_variables = ignore_private_variables
            self.ignore_nan_inequality = ignore_nan_inequality
            self.hasher = hasher

            self.significant_digits = self.get_significant_digits(significant_digits, ignore_numeric_type_changes)
            self.number_format_notation = number_format_notation
            self.verbose_level = verbose_level
            self.view = view
            # Setting up the cache for dynamic programming. One dictionary per instance of root of DeepDiff running.
            self.max_passes = max_passes
            self.max_diffs = max_diffs
            self.cutoff_distance_for_pairs = cutoff_distance_for_pairs
            # _deep_distance_buckets_exponent is only used for the number of buckets of distances when doing ignore_order=True calculations
            # The actual number of buckets will be 10 to the power of the _deep_distance_buckets_exponent
            self._deep_distance_buckets_exponent = len(str(self.max_passes)) + 3  # Adding some padding to it.
            # Parameters are the clean parameters to initialize DeepDiff with so we avoid all the above
            # cleaning functionalities when running DeepDiff recursively.
            # However DeepHash has its own set of parameters that are slightly different than DeepDIff.
            # DeepDiff parameters are transformed to DeepHash parameters via __get_deephash_params method.
            parameters = self.__dict__.copy()

        _purge_cache = True
        if _stats:
            # We are in some pass other than root
            self.is_root = False
            self._stats = _stats
            self._cache = _cache
            repeated_timer = None
        else:
            # we are at the root
            self.is_root = True
            # keep the cache. Only used for debugging what was in the cache.
            if _cache == 'keep':
                _purge_cache = False
            # Caching the DeepDiff results for dynamic programming
            self._cache = defaultdict(lambda: defaultdict(OrderedSet))
            self._stats = {
                PASSES_COUNT: 0,
                DIFF_COUNT: 0,
                CACHE_LEVEL_HIT: 0,
                DISTANCE_CACHE_HIT: 0,
                MAX_PASS_LIMIT_REACHED: False,
                MAX_DIFF_LIMIT_REACHED: False}
            if log_frequency_in_sec:
                # Creating a progress log reporter that runs in a separate thread every log_frequency_in_sec seconds.
                repeated_timer = RepeatedTimer(log_frequency_in_sec, _report_progress, self._stats, progress_logger)
            else:
                repeated_timer = None
        self.hashes = {} if hashes is None else hashes
        self.parameters = parameters
        self.deephash_parameters = self.__get_deephash_params()
        self.tree = TreeResult()
        self.t1 = t1
        self.t2 = t2

        self.numpy_used = False

        try:
            root = DiffLevel(t1, t2, verbose_level=self.verbose_level)
            self.__diff(root, parents_ids=frozenset({id(t1)}))

            self.tree.remove_empty_keys()
            view_results = self._get_view_results(self.view)
            self.update(view_results)
        finally:
            if self.is_root:
                if _purge_cache:
                    del self._cache
            if repeated_timer:
                repeated_timer.stop()

    def __get_deephash_params(self):
        result = {key: self.parameters[key] for key in (
            'exclude_types',
            'exclude_paths',
            'exclude_regex_paths',
            'hasher',
            'significant_digits',
            'number_format_notation',
            'ignore_string_type_changes',
            'ignore_numeric_type_changes',
            'ignore_type_in_groups',
            'ignore_type_subclasses',
            'ignore_string_case',
            'exclude_obj_callback',
            'ignore_private_variables',)}
        result['ignore_repetition'] = not self.report_repetition
        result['number_to_string_func'] = self.number_to_string
        return result

    def __report_result(self, report_type, level):
        """
        Add a detected change to the reference-style result dictionary.
        report_type will be added to level.
        (We'll create the text-style report from there later.)
        :param report_type: A well defined string key describing the type of change.
                            Examples: "set_item_added", "values_changed"
        :param parent: A DiffLevel object describing the objects in question in their
                       before-change and after-change object structure.

        :rtype: None
        """

        if not self.__skip_this(level):
            level.report_type = report_type
            self.tree[report_type].add(level)

            parent_level = level.up
            if parent_level:
                cache_key = parent_level.get_cache_key(self.hashes)
                self._cache[cache_key][report_type].add(level)

    @staticmethod
    def __dict_from_slots(object):
        def unmangle(attribute):
            if attribute.startswith('__') and attribute != '__weakref__':
                return '_{type}{attribute}'.format(
                    type=type(object).__name__,
                    attribute=attribute
                )
            return attribute

        all_slots = []

        if isinstance(object, type):
            mro = object.__mro__  # pragma: no cover. I have not been able to write a test for this case. But we still check for it.
        else:
            mro = object.__class__.__mro__

        for type_in_mro in mro:
            slots = getattr(type_in_mro, '__slots__', None)
            if slots:
                if isinstance(slots, strings):
                    all_slots.append(slots)
                else:
                    all_slots.extend(slots)

        return {i: getattr(object, unmangle(i)) for i in all_slots}

    def __diff_obj(self, level, parents_ids=frozenset({}),
                   is_namedtuple=False):
        """Difference of 2 objects"""
        try:
            if is_namedtuple:
                t1 = level.t1._asdict()
                t2 = level.t2._asdict()
            else:
                t1 = level.t1.__dict__
                t2 = level.t2.__dict__
        except AttributeError:
            try:
                t1 = self.__dict_from_slots(level.t1)
                t2 = self.__dict_from_slots(level.t2)
            except AttributeError:
                self.__report_result('unprocessed', level)
                return

        self.__diff_dict(
            level,
            parents_ids,
            print_as_attribute=True,
            override=True,
            override_t1=t1,
            override_t2=t2)

    def __skip_this(self, level):
        """
        Check whether this comparison should be skipped because one of the objects to compare meets exclusion criteria.
        :rtype: bool
        """
        skip = False
        if self.exclude_paths and level.path() in self.exclude_paths:
            skip = True
        elif self.exclude_regex_paths and any(
                [exclude_regex_path.search(level.path()) for exclude_regex_path in self.exclude_regex_paths]):
            skip = True
        elif self.exclude_types_tuple and \
                (isinstance(level.t1, self.exclude_types_tuple) or isinstance(level.t2, self.exclude_types_tuple)):
            skip = True
        elif self.exclude_obj_callback and \
                (self.exclude_obj_callback(level.t1, level.path()) or self.exclude_obj_callback(level.t2, level.path())):
            skip = True

        return skip

    def __get_clean_to_keys_mapping(self, keys, level):
        """
        Get a dictionary of cleaned value of keys to the keys themselves.
        This is mainly used to transform the keys when the type changes of keys should be ignored.

        TODO: needs also some key conversion for groups of types other than the built-in strings and numbers.
        """
        result = {}
        for key in keys:
            if self.ignore_string_type_changes and isinstance(key, bytes):
                clean_key = key.decode('utf-8')
            elif isinstance(key, numbers):
                type_ = "number" if self.ignore_numeric_type_changes else key.__class__.__name__
                clean_key = self.number_to_string(key, significant_digits=self.significant_digits,
                                                  number_format_notation=self.number_format_notation)
                clean_key = KEY_TO_VAL_STR.format(type_, clean_key)
            else:
                clean_key = key
            if clean_key in result:
                logger.warning(('{} and {} in {} become the same key when ignore_numeric_type_changes'
                                'or ignore_numeric_type_changes are set to be true.').format(
                                    key, result[clean_key], level.path()))
            else:
                result[clean_key] = key
        return result

    def __diff_dict(self,
                    level,
                    parents_ids=frozenset({}),
                    print_as_attribute=False,
                    override=False,
                    override_t1=None,
                    override_t2=None):
        """Difference of 2 dictionaries"""
        if override:
            # for special stuff like custom objects and named tuples we receive preprocessed t1 and t2
            # but must not spoil the chain (=level) with it
            t1 = override_t1
            t2 = override_t2
        else:
            t1 = level.t1
            t2 = level.t2

        if print_as_attribute:
            item_added_key = "attribute_added"
            item_removed_key = "attribute_removed"
            rel_class = AttributeRelationship
        else:
            item_added_key = "dictionary_item_added"
            item_removed_key = "dictionary_item_removed"
            rel_class = DictRelationship

        if self.ignore_private_variables:
            t1_keys = {key for key in t1 if not(isinstance(key, str) and key.startswith('__'))}
            t2_keys = {key for key in t2 if not(isinstance(key, str) and key.startswith('__'))}
        else:
            t1_keys = set(t1.keys())
            t2_keys = set(t2.keys())
        if self.ignore_string_type_changes or self.ignore_numeric_type_changes:
            t1_clean_to_keys = self.__get_clean_to_keys_mapping(keys=t1_keys, level=level)
            t2_clean_to_keys = self.__get_clean_to_keys_mapping(keys=t2_keys, level=level)
            t1_keys = set(t1_clean_to_keys.keys())
            t2_keys = set(t2_clean_to_keys.keys())
        else:
            t1_clean_to_keys = t2_clean_to_keys = None

        t_keys_intersect = t2_keys.intersection(t1_keys)

        t_keys_added = t2_keys - t_keys_intersect
        t_keys_removed = t1_keys - t_keys_intersect

        for key in t_keys_added:
            if self.__count_diff() is StopIteration:
                return

            key = t2_clean_to_keys[key] if t2_clean_to_keys else key
            change_level = level.branch_deeper(
                notpresent,
                t2[key],
                child_relationship_class=rel_class,
                child_relationship_param=key)
            self.__report_result(item_added_key, change_level)

        for key in t_keys_removed:
            if self.__count_diff() is StopIteration:
                return  # pragma: no cover. This is already covered for addition.

            key = t1_clean_to_keys[key] if t1_clean_to_keys else key
            change_level = level.branch_deeper(
                t1[key],
                notpresent,
                child_relationship_class=rel_class,
                child_relationship_param=key)
            self.__report_result(item_removed_key, change_level)

        for key in t_keys_intersect:  # key present in both dicts - need to compare values
            if self.__count_diff() is StopIteration:
                return

            key1 = t1_clean_to_keys[key] if t1_clean_to_keys else key
            key2 = t2_clean_to_keys[key] if t2_clean_to_keys else key
            item_id = id(t1[key1])
            if parents_ids and item_id in parents_ids:
                continue
            parents_ids_added = add_to_frozen_set(parents_ids, item_id)

            # Go one level deeper
            next_level = level.branch_deeper(
                t1[key1],
                t2[key2],
                child_relationship_class=rel_class,
                child_relationship_param=key)
            self.__diff(next_level, parents_ids_added)

    def __diff_set(self, level):
        """Difference of sets"""
        t1_hashtable = self.__create_hashtable(level, 't1')
        t2_hashtable = self.__create_hashtable(level, 't2')

        t1_hashes = set(t1_hashtable.keys())
        t2_hashes = set(t2_hashtable.keys())

        hashes_added = t2_hashes - t1_hashes
        hashes_removed = t1_hashes - t2_hashes

        items_added = [t2_hashtable[i].item for i in hashes_added]
        items_removed = [t1_hashtable[i].item for i in hashes_removed]

        for item in items_added:
            if self.__count_diff() is StopIteration:
                return  # pragma: no cover. This is already covered for addition.

            change_level = level.branch_deeper(
                notpresent, item, child_relationship_class=SetRelationship)
            self.__report_result('set_item_added', change_level)

        for item in items_removed:
            if self.__count_diff() is StopIteration:
                return  # pragma: no cover. This is already covered for addition.

            change_level = level.branch_deeper(
                item, notpresent, child_relationship_class=SetRelationship)
            self.__report_result('set_item_removed', change_level)

    @staticmethod
    def __iterables_subscriptable(t1, t2):
        try:
            if getattr(t1, '__getitem__') and getattr(t2, '__getitem__'):
                return True
            else:  # pragma: no cover
                return False  # should never happen
        except AttributeError:
            return False

    def __diff_iterable(self, level, parents_ids=frozenset({})):
        """Difference of iterables"""
        if self.ignore_order:
            self.__diff_iterable_with_deephash(level, parents_ids)
        else:
            self.__diff_iterable_in_order(level, parents_ids)

    def __diff_iterable_in_order(self, level, parents_ids=frozenset({})):
        # We're handling both subscriptable and non-subscriptable iterables. Which one is it?
        subscriptable = self.__iterables_subscriptable(level.t1, level.t2)
        if subscriptable:
            child_relationship_class = SubscriptableIterableRelationship
        else:
            child_relationship_class = NonSubscriptableIterableRelationship

        for i, (x, y) in enumerate(
                zip_longest(
                    level.t1, level.t2, fillvalue=ListItemRemovedOrAdded)):

            if self.__count_diff() is StopIteration:
                return  # pragma: no cover. This is already covered for addition.

            if y is ListItemRemovedOrAdded:  # item removed completely
                change_level = level.branch_deeper(
                    x,
                    notpresent,
                    child_relationship_class=child_relationship_class,
                    child_relationship_param=i)
                self.__report_result('iterable_item_removed', change_level)

            elif x is ListItemRemovedOrAdded:  # new item added
                change_level = level.branch_deeper(
                    notpresent,
                    y,
                    child_relationship_class=child_relationship_class,
                    child_relationship_param=i)
                self.__report_result('iterable_item_added', change_level)

            else:  # check if item value has changed
                item_id = id(x)
                if parents_ids and item_id in parents_ids:
                    continue
                parents_ids_added = add_to_frozen_set(parents_ids, item_id)

                # Go one level deeper
                next_level = level.branch_deeper(
                    x,
                    y,
                    child_relationship_class=child_relationship_class,
                    child_relationship_param=i)
                self.__diff(next_level, parents_ids_added)

    def __diff_str(self, level):
        """Compare strings"""
        if self.ignore_string_case:
            level.t1 = level.t1.lower()
            level.t2 = level.t2.lower()

        if type(level.t1) == type(level.t2) and level.t1 == level.t2:  # NOQA
            return

        # do we add a diff for convenience?
        do_diff = True
        t1_str = level.t1
        t2_str = level.t2

        if isinstance(level.t1, bytes_type):
            try:
                t1_str = level.t1.decode('ascii')
            except UnicodeDecodeError:
                do_diff = False

        if isinstance(level.t2, bytes_type):
            try:
                t2_str = level.t2.decode('ascii')
            except UnicodeDecodeError:
                do_diff = False

        if t1_str == t2_str:
            return

        if do_diff:
            if '\n' in t1_str or '\n' in t2_str:
                diff = difflib.unified_diff(
                    t1_str.splitlines(), t2_str.splitlines(), lineterm='')
                diff = list(diff)
                if diff:
                    level.additional['diff'] = '\n'.join(diff)

        self.__report_result('values_changed', level)

    def __diff_tuple(self, level, parents_ids):
        # Checking to see if it has _fields. Which probably means it is a named
        # tuple.
        try:
            level.t1._asdict
        # It must be a normal tuple
        except AttributeError:
            self.__diff_iterable(level, parents_ids)
        # We assume it is a namedtuple then
        else:
            self.__diff_obj(level, parents_ids, is_namedtuple=True)

    def _add_hash(self, hashes, item_hash, item, i):
        if item_hash in hashes:
            hashes[item_hash].indexes.append(i)
        else:
            hashes[item_hash] = IndexedHash(indexes=[i], item=item)

    def __create_hashtable(self, level, t):
        """Create hashtable of {item_hash: (indexes, item)}"""
        obj = getattr(level, t)

        local_hashes = {}
        for (i, item) in enumerate(obj):
            try:
                parent = "{}[{}]".format(level.path(), i)
                # Note: in the DeepDiff we only calculate the hash of items when we have to.
                # So self.hashes does not include hashes of all objects in t1 and t2.
                # It only includes the ones needed when comparing iterables.
                # The self.hashes dictionary gets shared between different runs of DeepHash
                # So that any object that is already calculated to have a hash is not re-calculated.
                hashes_all = DeepHash(item,
                                      hashes=self.hashes,
                                      parent=parent,
                                      apply_hash=True,
                                      **self.deephash_parameters,
                                      )
                item_hash = hashes_all[item]
            except Exception as e:  # pragma: no cover
                logger.error("Can not produce a hash for %s."
                             "Not counting this object.\n %s" %
                             (level.path(), e))
            else:
                if item_hash is unprocessed:  # pragma: no cover
                    logger.warning("Item %s was not processed while hashing "
                                   "thus not counting this object." %
                                   level.path())
                else:
                    self._add_hash(hashes=local_hashes, item_hash=item_hash, item=item, i=i)

        # Also we hash the iterables themselves too so that we can later create cache keys from those hashes.
        try:
            DeepHash(
                obj,
                hashes=self.hashes,
                parent=level.path(),
                apply_hash=True,
                **self.deephash_parameters,
            )
        except Exception as e:  # pragma: no cover
            logger.error("Can not produce a hash for iterable %s. %s" %
                         (level.path(), e))
        return local_hashes

    def __get_and_cache_rough_distance(self, added_hash, removed_hash, added_hash_obj, removed_hash_obj):
        # We need the rough distance between the 2 objects to see if they qualify to be pairs or not
        cache_key = 'distance_cache' + str(default_hasher(hex(added_hash).encode('utf-8') + b'--' + hex(removed_hash).encode('utf-8')))
        if cache_key in self._cache:
            self._stats[DISTANCE_CACHE_HIT] += 1
            _distance = self._cache[cache_key]
        else:
            _distance = get_numeric_types_distance(
                removed_hash_obj.item, added_hash_obj.item, max_=self.cutoff_distance_for_pairs)
            if _distance is not_found:
                # We can only cache the rough distance and not the actual diff result for reuse.
                # The reason is that we have modified the parameters explicitly so they are different and can't
                # be used for diff reporting
                diff = DeepDiff(
                    removed_hash_obj.item, added_hash_obj.item,
                    parameters=self.parameters, hashes=self.hashes, _stats=self._stats, _cache=self._cache, view=DELTA_VIEW)
                _distance = diff.get_deep_distance()
            _distance = Decimal(self.number_to_string(
                _distance,
                significant_digits=self._deep_distance_buckets_exponent,
                number_format_notation=self.number_format_notation))
            self._cache[cache_key] = _distance
        return _distance

    def __get_most_in_common_pairs_in_iterables(self, hashes_added, hashes_removed, t1_hashtable, t2_hashtable):
        """
        Get the closest pairs between items that are removed and items that are added.

        Note that due to the current reporting structure in DeepDiff, we don't compare an item that
        was added to an item that is in both t1 and t2.

        For example

        [{1, 2}, {4, 5, 6}]
        [{1, 2}, {1, 2, 3}]

        is only compared between {4, 5, 6} and {1, 2, 3} even though technically {1, 2, 3} is
        just one item different than {1, 2}

        Perhaps in future we can have a report key that is item duplicated and modified instead of just added.
        """
        cache_key = combine_hashes_lists(items=[hashes_added, hashes_removed], prefix='pairs_cache')
        if cache_key in self._cache:
            return self._cache[cache_key].copy()

        # A dictionary of hashes to distances and each distance to an ordered set of hashes.
        # It tells us about the distance of each object from other objects.
        # And the objects with the same distances are grouped together in an ordered set.
        # It also includes a "max" key that is just the value of the biggest current distance in the
        # most_in_common_pairs dictionary.
        most_in_common_pairs = defaultdict(lambda: defaultdict(OrderedSetPlus))
        pairs = {}

        for added_hash in hashes_added:
            for removed_hash in hashes_removed:
                added_hash_obj = t2_hashtable[added_hash]
                removed_hash_obj = t1_hashtable[removed_hash]

                _distance = self.__get_and_cache_rough_distance(
                    added_hash, removed_hash, added_hash_obj, removed_hash_obj)
                # Left for future debugging
                # print(f'{bcolors.HEADER}distance of {added_hash_obj.item} and {removed_hash_obj.item}: {_distance}{bcolors.ENDC}')
                # Discard potential pairs that are too far.
                if _distance >= self.cutoff_distance_for_pairs:
                    continue
                pairs_of_item = most_in_common_pairs[added_hash]
                pairs_of_item[_distance].add(removed_hash)
                count_of_distances = len(pairs_of_item)
                # There is a maximum number of distances we want to keep track of.
                current_max_distance_from_item = pairs_of_item.get('max', 0)
                if count_of_distances < self.MAX_COMMON_PAIR_DISTANCES:
                    pairs_of_item['max'] = max(_distance, current_max_distance_from_item)
                elif _distance <= current_max_distance_from_item:
                    if _distance < current_max_distance_from_item:
                        del pairs_of_item[current_max_distance_from_item]
                        pairs_of_item['max'] = _distance

        used_to_hashes = set()

        distances_to_from_hashes = defaultdict(OrderedSetPlus)
        for from_hash, distances_to_to_hashes in most_in_common_pairs.items():
            del distances_to_to_hashes['max']
            for dist in distances_to_to_hashes:
                distances_to_from_hashes[dist].add(from_hash)

        for dist in sorted(distances_to_from_hashes.keys()):
            from_hashes = distances_to_from_hashes[dist]
            while from_hashes:
                from_hash = from_hashes.lpop()
                if from_hash not in used_to_hashes:
                    to_hashes = most_in_common_pairs[from_hash][dist]
                    while to_hashes:
                        to_hash = to_hashes.lpop()
                        if to_hash not in used_to_hashes:
                            used_to_hashes.add(from_hash)
                            used_to_hashes.add(to_hash)
                            # Left for future debugging:
                            # print(f'{bcolors.FAIL}Adding {t2_hashtable[from_hash].item} as a pairs of {t1_hashtable[to_hash].item} with distance of {dist}{bcolors.ENDC}')
                            pairs[from_hash] = to_hash

        inverse_pairs = {v: k for k, v in pairs.items()}
        pairs.update(inverse_pairs)
        self._cache[cache_key] = pairs
        return pairs.copy()

    def __diff_iterable_with_deephash(self, level, parents_ids):
        """Diff of unhashable iterables. Only used when ignoring the order."""
        t1_hashtable = self.__create_hashtable(level, 't1')
        t2_hashtable = self.__create_hashtable(level, 't2')

        t1_hashes = OrderedSet(t1_hashtable.keys())
        t2_hashes = OrderedSet(t2_hashtable.keys())

        hashes_added = t2_hashes - t1_hashes
        hashes_removed = t1_hashes - t2_hashes

        if self._stats[PASSES_COUNT] < self.max_passes:
            self._stats[PASSES_COUNT] += 1
            pairs = self.__get_most_in_common_pairs_in_iterables(
                hashes_added, hashes_removed, t1_hashtable, t2_hashtable)
        else:
            if not self._stats[MAX_PASS_LIMIT_REACHED]:
                self._stats[MAX_PASS_LIMIT_REACHED] = True
                logger.warning(MAX_PASSES_REACHED_MSG.format(self.max_passes))
            pairs = {}

        def get_other_pair(hash_value, in_t1=True):
            """
            Gets the other paired indexed hash item to the hash_value in the pairs dictionary
            in_t1: are we looking for the other pair in t1 or t2?
            """
            if in_t1:
                hashtable = t1_hashtable
                the_other_hashes = hashes_removed
            else:
                hashtable = t2_hashtable
                the_other_hashes = hashes_added
            other = pairs.pop(hash_value, notpresent)
            if other is notpresent:
                other = notpresent_indexed
            else:
                # The pairs are symmetrical.
                # removing the other direction of pair
                # so it does not get used.
                del pairs[other]
                the_other_hashes.remove(other)
                other = hashtable[other]
            return other

        if self.report_repetition:
            for hash_value in hashes_added:
                if self.__count_diff() is StopIteration:
                    return
                other = get_other_pair(hash_value)
                item_id = id(other.item)
                if parents_ids and item_id in parents_ids:
                    continue
                indexes = t2_hashtable[hash_value].indexes if other.item is notpresent else other.indexes
                for i in indexes:
                    change_level = level.branch_deeper(
                        other.item,
                        t2_hashtable[hash_value].item,
                        child_relationship_class=SubscriptableIterableRelationship,
                        child_relationship_param=i
                    )
                    if other.item is notpresent:
                        self.__report_result('iterable_item_added', change_level)
                    else:
                        parents_ids_added = add_to_frozen_set(parents_ids, item_id)
                        self.__diff(change_level, parents_ids_added)
            for hash_value in hashes_removed:
                if self.__count_diff() is StopIteration:
                    return
                other = get_other_pair(hash_value, in_t1=False)
                for i in t1_hashtable[hash_value].indexes:
                    change_level = level.branch_deeper(
                        t1_hashtable[hash_value].item,
                        other.item,
                        child_relationship_class=SubscriptableIterableRelationship,
                        child_relationship_param=i)
                    if other.item is notpresent:
                        self.__report_result('iterable_item_removed', change_level)
                    else:
                        parents_ids_added = add_to_frozen_set(parents_ids, item_id)
                        self.__diff(change_level, parents_ids_added)

            items_intersect = t2_hashes.intersection(t1_hashes)

            for hash_value in items_intersect:
                t1_indexes = t1_hashtable[hash_value].indexes
                t2_indexes = t2_hashtable[hash_value].indexes
                t1_indexes_len = len(t1_indexes)
                t2_indexes_len = len(t2_indexes)
                if t1_indexes_len != t2_indexes_len:  # this is a repetition change!
                    # create "change" entry, keep current level untouched to handle further changes
                    repetition_change_level = level.branch_deeper(
                        t1_hashtable[hash_value].item,
                        t2_hashtable[hash_value].item,  # nb: those are equal!
                        child_relationship_class=SubscriptableIterableRelationship,
                        child_relationship_param=t1_hashtable[hash_value]
                        .indexes[0])
                    repetition_change_level.additional['repetition'] = RemapDict(
                        old_repeat=t1_indexes_len,
                        new_repeat=t2_indexes_len,
                        old_indexes=t1_indexes,
                        new_indexes=t2_indexes)
                    self.__report_result('repetition_change',
                                         repetition_change_level)

        else:
            for hash_value in hashes_added:
                if self.__count_diff() is StopIteration:
                    return
                other = get_other_pair(hash_value)
                item_id = id(other.item)
                if parents_ids and item_id in parents_ids:
                    continue
                index = t2_hashtable[hash_value].indexes[0] if other.item is notpresent else other.indexes[0]
                change_level = level.branch_deeper(
                    other.item,
                    t2_hashtable[hash_value].item,
                    child_relationship_class=SubscriptableIterableRelationship,
                    child_relationship_param=index)
                if other.item is notpresent:
                    self.__report_result('iterable_item_added', change_level)
                else:
                    parents_ids_added = add_to_frozen_set(parents_ids, item_id)
                    self.__diff(change_level, parents_ids_added)

            for hash_value in hashes_removed:
                if self.__count_diff() is StopIteration:
                    return
                other = get_other_pair(hash_value, in_t1=False)
                item_id = id(other.item)
                if parents_ids and item_id in parents_ids:
                    continue
                change_level = level.branch_deeper(
                    t1_hashtable[hash_value].item,
                    other.item,
                    child_relationship_class=SubscriptableIterableRelationship,
                    child_relationship_param=t1_hashtable[hash_value].indexes[
                        0])
                if other.item is notpresent:
                    self.__report_result('iterable_item_removed', change_level)
                else:
                    parents_ids_added = add_to_frozen_set(parents_ids, item_id)
                    self.__diff(change_level, parents_ids_added)

    def __diff_booleans(self, level):
        if level.t1 != level.t2:
            self.__report_result('values_changed', level)

    def __diff_numbers(self, level):
        """Diff Numbers"""
        t1_type = "number" if self.ignore_numeric_type_changes else level.t1.__class__.__name__
        t2_type = "number" if self.ignore_numeric_type_changes else level.t2.__class__.__name__

        if self.significant_digits is None:
            if level.t1 != level.t2:
                self.__report_result('values_changed', level)
        else:
            # Bernhard10: I use string formatting for comparison, to be consistent with usecases where
            # data is read from files that were previousely written from python and
            # to be consistent with on-screen representation of numbers.
            # Other options would be abs(t1-t2)<10**-self.significant_digits
            # or math.is_close (python3.5+)
            # Note that abs(3.25-3.251) = 0.0009999999999998899 < 0.001
            # Note also that "{:.3f}".format(1.1135) = 1.113, but "{:.3f}".format(1.11351) = 1.114
            # For Decimals, format seems to round 2.5 to 2 and 3.5 to 4 (to closest even number)
            t1_s = self.number_to_string(level.t1,
                                         significant_digits=self.significant_digits,
                                         number_format_notation=self.number_format_notation)
            t2_s = self.number_to_string(level.t2,
                                         significant_digits=self.significant_digits,
                                         number_format_notation=self.number_format_notation)

            t1_s = KEY_TO_VAL_STR.format(t1_type, t1_s)
            t2_s = KEY_TO_VAL_STR.format(t2_type, t2_s)
            if t1_s != t2_s:
                self.__report_result('values_changed', level)

    def __diff_numpy_array(self, level, parents_ids=frozenset({})):
        """Diff numpy arrays"""
        self.numpy_used = True
        if np is None:
            raise ImportError('Unable to import numpy. Please make sure it is installed.')

        if not self.ignore_order:
            # fast checks
            if self.significant_digits is None:
                if np.array_equal(level.t1, level.t2):
                    return  # all good
            else:
                try:
                    np.testing.assert_almost_equal(level.t1, level.t2, decimal=self.significant_digits)
                    return  # all good
                except AssertionError:
                    pass    # do detailed checking below

        # compare array meta-data
        if level.t1.shape != level.t2.shape:
            next_level = level.branch_deeper(
                level.t1.shape, level.t2.shape,
                child_relationship_class=AttributeRelationship,
                child_relationship_param='shape')
            self.__diff(next_level, parents_ids)
        else:
            # metadata same -- the difference is in the content
            shape = level.t1.shape
            dimensions = len(shape)
            if dimensions == 1:
                self.__diff_iterable(level, parents_ids)
            elif self.ignore_order:
                # convert to list
                level.t1 = level.t1.tolist()
                level.t2 = level.t2.tolist()
                self.__diff_iterable(level, parents_ids)
            else:
                for (t1_path, t1_row), (t2_path, t2_row) in zip(
                        get_numpy_ndarray_rows(level.t1, shape),
                        get_numpy_ndarray_rows(level.t2, shape)):

                    new_level = level.branch_deeper(
                        t1_row,
                        t2_row,
                        child_relationship_class=NumpyArrayRelationship,
                        child_relationship_param=t1_path)

                    self.__diff_iterable(new_level, parents_ids)

    def __diff_types(self, level):
        """Diff types"""
        level.report_type = 'type_changes'
        self.__report_result('type_changes', level)

    def __get_from_cache(self, level):
        cache_key = level.get_cache_key(self.hashes)
        cache_hit = False
        if cache_key in self._cache:
            cache_hit = True
            self._stats[CACHE_LEVEL_HIT] += 1
            for report_key, report_values in self._cache[cache_key].items():
                for report_level in report_values:
                    new_report = report_level.stitch_to_parent(level)
                    if new_report is not skipped:
                        self.tree[report_key].add(new_report)
        return cache_hit

    def __count_diff(self):
        if self.max_diffs is not None and self._stats[DIFF_COUNT] > self.max_diffs:
            if not self._stats[MAX_DIFF_LIMIT_REACHED]:
                self._stats[MAX_DIFF_LIMIT_REACHED] = True
                logger.warning(MAX_DIFFS_REACHED_MSG.format(self.max_diffs))
            return StopIteration
        self._stats[DIFF_COUNT] += 1

    def __diff(self, level, parents_ids=frozenset({})):
        """The main diff method"""
        if self.__count_diff() is StopIteration:
            return

        cache_hit = self.__get_from_cache(level)
        if cache_hit:
            return

        if level.t1 is level.t2:
            return

        if self.__skip_this(level):
            return

        if get_type(level.t1) != get_type(level.t2):
            report_type_change = True
            for type_group in self.ignore_type_in_groups:
                if self.type_check_func(level.t1, type_group) and self.type_check_func(level.t2, type_group):
                    report_type_change = False
                    break
            if report_type_change:
                self.__diff_types(level)
                return

        if self.ignore_nan_inequality and isinstance(level.t1, float) and str(level.t1) == str(level.t2) == 'nan':
            return

        if isinstance(level.t1, booleans):
            self.__diff_booleans(level)

        if isinstance(level.t1, strings):
            self.__diff_str(level)

        elif isinstance(level.t1, numbers):
            self.__diff_numbers(level)

        elif isinstance(level.t1, Mapping):
            self.__diff_dict(level, parents_ids)

        elif isinstance(level.t1, tuple):
            self.__diff_tuple(level, parents_ids)

        elif isinstance(level.t1, (set, frozenset, OrderedSet)):
            self.__diff_set(level)

        elif isinstance(level.t1, np_ndarray):
            self.__diff_numpy_array(level, parents_ids)

        elif isinstance(level.t1, Iterable):
            self.__diff_iterable(level, parents_ids)

        else:
            self.__diff_obj(level, parents_ids)

    def _get_view_results(self, view):
        """
        Get the results based on the view
        """
        result = self.tree
        if not self.report_repetition:
            result.mutual_add_removes_to_become_value_changes()
        if view == TREE_VIEW:
            pass
        elif view == TEXT_VIEW:
            result = TextResult(tree_results=self.tree, verbose_level=self.verbose_level)
            result.remove_empty_keys()
        elif view == DELTA_VIEW:
            result = self._to_delta_dict(report_repetition_required=False)
        else:
            raise ValueError('The only valid values for the view parameter are text and tree.')
        return result

    def get_stats(self):
        """
        Get some stats on internals of the DeepDiff run.
        """
        return self._stats


if __name__ == "__main__":  # pragma: no cover
    import doctest
    doctest.testmod()
