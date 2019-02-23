#!/usr/bin/env python
# -*- coding: utf-8 -*-

# In order to run the docstrings:
# python3 -m deepdiff.diff
# You might need to run it many times since dictionaries come in different orders
# every time you run the docstrings.
# However the docstring expects it in a specific order in order to pass!

import difflib
import logging
import json
import jsonpickle
import warnings

from decimal import Decimal
from itertools import zip_longest
from collections.abc import Mapping, Iterable

from ordered_set import OrderedSet

from deepdiff.helper import (strings, bytes_type, numbers, ListItemRemovedOrAdded, notpresent,
                             IndexedHash, Verbose, unprocessed, json_convertor_default, add_to_frozen_set,
                             convert_item_or_items_into_set_else_none,
                             convert_item_or_items_into_compiled_regexes_else_none)
from deepdiff.model import RemapDict, ResultDict, TextResult, TreeResult, DiffLevel
from deepdiff.model import DictRelationship, AttributeRelationship
from deepdiff.model import SubscriptableIterableRelationship, NonSubscriptableIterableRelationship, SetRelationship
from deepdiff.deephash import DeepHash

logger = logging.getLogger(__name__)
warnings.simplefilter('once', DeprecationWarning)

TREE_VIEW = 'tree'
TEXT_VIEW = 'text'


class DeepDiff(ResultDict):
    numbers = numbers
    strings = strings

    def __init__(self,
                 t1,
                 t2,
                 ignore_order=False,
                 ignore_type_in_groups=None,
                 report_repetition=False,
                 significant_digits=None,
                 exclude_paths=None,
                 exclude_regex_paths=None,
                 exclude_types=None,
                 ignore_string_type_changes=None,
                 include_numeric_type_changes=True,
                 verbose_level=1,
                 view=TEXT_VIEW,
                 hasher=DeepHash.murmur3_128bit,
                 transformer=None,
                 **kwargs):
        if kwargs:
            raise ValueError((
                "The following parameter(s) are not valid: %s\n"
                "The valid parameters are ignore_order, report_repetition, significant_digits, ignore_type_in_groups"
                "exclude_paths, exclude_types, exclude_regex_paths, transformer, verbose_level and view.") % ', '.join(kwargs.keys()))

        self.ignore_order = ignore_order
        if ignore_string_type_changes is not None and ignore_type_in_groups is not None:
            raise ValueError('Please set either ignore_string_type_changes or ignore_type_in_groups but not both.')
        if ignore_type_in_groups is None and ignore_string_type_changes is None:
            ignore_string_type_changes = True
        self.ignore_type_in_groups = self._get_ignore_types_in_groups(
            ignore_type_in_groups,
            ignore_string_type_changes, include_numeric_type_changes)
        self.report_repetition = report_repetition
        self.exclude_paths = convert_item_or_items_into_set_else_none(exclude_paths)
        self.exclude_regex_paths = convert_item_or_items_into_compiled_regexes_else_none(exclude_regex_paths)
        self.exclude_types = set(exclude_types) if exclude_types else None
        self.exclude_types_tuple = tuple(exclude_types) if exclude_types else None  # we need tuple for checking isinstance
        self.ignore_string_type_changes = ignore_string_type_changes
        self.include_numeric_type_changes = include_numeric_type_changes
        self.hashes = {}
        self.hasher = hasher

        if significant_digits is not None and significant_digits < 0:
            raise ValueError(
                "significant_digits must be None or a non-negative integer")
        self.significant_digits = significant_digits

        self.tree = TreeResult()

        Verbose.level = verbose_level

        if transformer:
            t1 = transformer(t1)
            t2 = transformer(t2)

        root = DiffLevel(t1, t2)
        self.__diff(root, parents_ids=frozenset({id(t1)}))

        self.tree.cleanup()

        self.view = view
        view_results = self._get_view_results(view)
        self.update(view_results)

    def _get_ignore_types_in_groups(self, ignore_type_in_groups,
                                    ignore_string_type_changes, include_numeric_type_changes):
        if ignore_type_in_groups:
            if isinstance(ignore_type_in_groups[0], type):
                ignore_type_in_groups = [tuple(ignore_type_in_groups)]
            else:
                ignore_type_in_groups = list(map(tuple, ignore_type_in_groups))
        else:
            ignore_type_in_groups = []

        if ignore_string_type_changes:
            ignore_type_in_groups.append(self.strings)

        if not include_numeric_type_changes:
            ignore_type_in_groups.append(self.numbers)

        return ignore_type_in_groups

    def _get_view_results(self, view):
        """
        Get the results based on the view
        """
        if view == TREE_VIEW:
            result = self.tree
        else:
            result = TextResult(tree_results=self.tree)
            result.cleanup()  # clean up text-style result dictionary
        return result

    # TODO: adding adding functionality
    # def __add__(self, other):
    #     if isinstance(other, DeepDiff):
    #         result = deepcopy(self)
    #         result.update(other)
    #     else:
    #         result = deepcopy(other)
    #         for key in REPORT_KEYS:
    #             if key in self:
    #                 getattr(self, "_do_{}".format(key))(result)

    #     return result

    # __radd__ = __add__

    # def _do_iterable_item_added(self, result):
    #     for item in self['iterable_item_added']:
    #         pass

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
            mro = object.__mro__
        else:
            mro = object.__class__.__mro__

        for type_in_mro in mro:
            slots = getattr(type_in_mro, '__slots__', ())
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
        else:
            if self.exclude_types_tuple and (isinstance(level.t1, self.exclude_types_tuple) or
                                             isinstance(level.t2, self.exclude_types_tuple)):
                skip = True

        return skip

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

        t1_keys = set(t1.keys())
        t2_keys = set(t2.keys())

        t_keys_intersect = t2_keys.intersection(t1_keys)

        t_keys_added = t2_keys - t_keys_intersect
        t_keys_removed = t1_keys - t_keys_intersect

        for key in t_keys_added:
            change_level = level.branch_deeper(
                notpresent,
                t2[key],
                child_relationship_class=rel_class,
                child_relationship_param=key)
            self.__report_result(item_added_key, change_level)

        for key in t_keys_removed:
            change_level = level.branch_deeper(
                t1[key],
                notpresent,
                child_relationship_class=rel_class,
                child_relationship_param=key)
            self.__report_result(item_removed_key, change_level)

        for key in t_keys_intersect:  # key present in both dicts - need to compare values
            item_id = id(t1[key])
            if parents_ids and item_id in parents_ids:
                continue
            parents_ids_added = add_to_frozen_set(parents_ids, item_id)

            # Go one level deeper
            next_level = level.branch_deeper(
                t1[key],
                t2[key],
                child_relationship_class=rel_class,
                child_relationship_param=key)
            self.__diff(next_level, parents_ids_added)

    def __diff_set(self, level):
        """Difference of sets"""
        t1_hashtable = self.__create_hashtable(level.t1, level)
        t2_hashtable = self.__create_hashtable(level.t2, level)

        t1_hashes = set(t1_hashtable.keys())
        t2_hashes = set(t2_hashtable.keys())

        hashes_added = t2_hashes - t1_hashes
        hashes_removed = t1_hashes - t2_hashes

        items_added = [t2_hashtable[i].item for i in hashes_added]
        items_removed = [t1_hashtable[i].item for i in hashes_removed]

        for item in items_added:
            change_level = level.branch_deeper(
                notpresent, item, child_relationship_class=SetRelationship)
            self.__report_result('set_item_added', change_level)

        for item in items_removed:
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
        # We're handling both subscriptable and non-subscriptable iterables. Which one is it?
        subscriptable = self.__iterables_subscriptable(level.t1, level.t2)
        if subscriptable:
            child_relationship_class = SubscriptableIterableRelationship
        else:
            child_relationship_class = NonSubscriptableIterableRelationship

        for i, (x, y) in enumerate(
                zip_longest(
                    level.t1, level.t2, fillvalue=ListItemRemovedOrAdded)):
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
        if type(level.t1) == type(level.t2) and level.t1 == level.t2:
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
            if u'\n' in t1_str or u'\n' in t2_str:
                diff = difflib.unified_diff(
                    t1_str.splitlines(), t2_str.splitlines(), lineterm='')
                diff = list(diff)
                if diff:
                    level.additional['diff'] = u'\n'.join(diff)

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

    def __create_hashtable(self, t, level):
        """Create hashtable of {item_hash: (indexes, item)}"""

        hashes = {}
        for (i, item) in enumerate(t):
            try:
                hashes_all = DeepHash(item,
                                      hashes=self.hashes,
                                      exclude_types=self.exclude_types,
                                      significant_digits=self.significant_digits,
                                      ignore_string_type_changes=self.ignore_string_type_changes,
                                      hasher=self.hasher)
                item_hash = hashes_all.get(id(item), item)
            except Exception as e:  # pragma: no cover
                logger.warning("Can not produce a hash for %s."
                               "Not counting this object.\n %s" %
                               (level.path(), e))
            else:
                if item_hash is unprocessed:  # pragma: no cover
                    logger.warning("Item %s was not processed while hashing "
                                   "thus not counting this object." %
                                   level.path())
                else:
                    self._add_hash(hashes=hashes, item_hash=item_hash, item=item, i=i)
        return hashes

    def __diff_iterable_with_deephash(self, level):
        """Diff of unhashable iterables. Only used when ignoring the order."""
        t1_hashtable = self.__create_hashtable(level.t1, level)
        t2_hashtable = self.__create_hashtable(level.t2, level)

        t1_hashes = set(t1_hashtable.keys())
        t2_hashes = set(t2_hashtable.keys())

        hashes_added = t2_hashes - t1_hashes
        hashes_removed = t1_hashes - t2_hashes

        if self.report_repetition:
            for hash_value in hashes_added:
                for i in t2_hashtable[hash_value].indexes:
                    change_level = level.branch_deeper(
                        notpresent,
                        t2_hashtable[hash_value].item,
                        child_relationship_class=SubscriptableIterableRelationship,  # TODO: that might be a lie!
                        child_relationship_param=i
                    )  # TODO: what is this value exactly?
                    self.__report_result('iterable_item_added', change_level)

            for hash_value in hashes_removed:
                for i in t1_hashtable[hash_value].indexes:
                    change_level = level.branch_deeper(
                        t1_hashtable[hash_value].item,
                        notpresent,
                        child_relationship_class=SubscriptableIterableRelationship,  # TODO: that might be a lie!
                        child_relationship_param=i)
                    self.__report_result('iterable_item_removed', change_level)

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
                        child_relationship_class=SubscriptableIterableRelationship,  # TODO: that might be a lie!
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
                change_level = level.branch_deeper(
                    notpresent,
                    t2_hashtable[hash_value].item,
                    child_relationship_class=SubscriptableIterableRelationship,  # TODO: that might be a lie!
                    child_relationship_param=t2_hashtable[hash_value].indexes[
                        0])  # TODO: what is this value exactly?
                self.__report_result('iterable_item_added', change_level)

            for hash_value in hashes_removed:
                change_level = level.branch_deeper(
                    t1_hashtable[hash_value].item,
                    notpresent,
                    child_relationship_class=SubscriptableIterableRelationship,  # TODO: that might be a lie!
                    child_relationship_param=t1_hashtable[hash_value].indexes[
                        0])
                self.__report_result('iterable_item_removed', change_level)

    def __diff_numbers(self, level):
        """Diff Numbers"""

        if self.significant_digits is not None and isinstance(level.t1, (
                float, complex, Decimal)):
            # Bernhard10: I use string formatting for comparison, to be consistent with usecases where
            # data is read from files that were previousely written from python and
            # to be consistent with on-screen representation of numbers.
            # Other options would be abs(t1-t2)<10**-self.significant_digits
            # or math.is_close (python3.5+)
            # Note that abs(3.25-3.251) = 0.0009999999999998899 < 0.001
            # Note also that "{:.3f}".format(1.1135) = 1.113, but "{:.3f}".format(1.11351) = 1.114
            # For Decimals, format seems to round 2.5 to 2 and 3.5 to 4 (to closest even number)
            t1_s = ("{:.%sf}" % self.significant_digits).format(level.t1)
            t2_s = ("{:.%sf}" % self.significant_digits).format(level.t2)

            # Special case for 0: "-0.00" should compare equal to "0.00"
            if set(t1_s) <= set("-0.") and set(t2_s) <= set("-0."):
                return
            elif t1_s != t2_s:
                self.__report_result('values_changed', level)
        else:
            if level.t1 != level.t2:
                self.__report_result('values_changed', level)

    def __diff_types(self, level):
        """Diff types"""
        level.report_type = 'type_changes'
        self.__report_result('type_changes', level)

    def __diff(self, level, parents_ids=frozenset({})):
        """The main diff method"""
        if level.t1 is level.t2:
            return

        if self.__skip_this(level):
            return

        if type(level.t1) != type(level.t2):  # NOQA
            report_type_change = True
            for type_group in self.ignore_type_in_groups:
                if isinstance(level.t1, type_group) and isinstance(level.t2, type_group):
                    report_type_change = False
                    break
            if report_type_change:
                self.__diff_types(level)
                return

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

        elif isinstance(level.t1, Iterable):
            if self.ignore_order:
                self.__diff_iterable_with_deephash(level)
            else:
                self.__diff_iterable(level, parents_ids)

        else:
            self.__diff_obj(level, parents_ids)

        return

    @property
    def json(self):
        warnings.warn(
            "json property will be deprecated. Instead use: to_json_pickle() to get the json pickle or to_json() for bare-bone json.",
            DeprecationWarning
        )
        if not hasattr(self, '_json'):
            # copy of self removes all the extra attributes since it assumes
            # we have only a simple dictionary.
            copied = self.copy()
            self._json = jsonpickle.encode(copied)
        return self._json

    def to_json_pickle(self):
        """
        Get the json pickle of the diff object. Unless you need all the attributes and functionality of DeepDiff, doing to_json is the safer option that json pickle.
        """
        copied = self.copy()
        return jsonpickle.encode(copied)

    @json.deleter
    def json(self):
        del self._json

    @classmethod
    def from_json(cls, value):
        warnings.warn(
            "from_json is renamed to from_json_pickle",
            DeprecationWarning
        )
        return cls.from_json_pickle(value)

    @classmethod
    def from_json_pickle(cls, value):
        """
        Load DeepDiff object with all the bells and whistles from the json pickle dump.
        Note that json pickle dump comes from to_json_pickle
        """
        return jsonpickle.decode(value)

    def to_json(self, default_mapping=None):
        """
        Dump json of the text view
        """
        return json.dumps(self.to_dict(), default=json_convertor_default(default_mapping=default_mapping))

    def to_dict(self):
        """
        Dump dictionary of the text view
        """
        if self.view == TREE_VIEW:
            result = dict(self._get_view_results(view=TEXT_VIEW))
        else:
            result = dict(self)
        return result


if __name__ == "__main__":  # pragma: no cover
    import doctest
    doctest.testmod()
