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
import os

from decimal import Decimal
from itertools import zip_longest
from collections.abc import Mapping, Iterable

from ordered_set import OrderedSet

from deepdiff.helper import (strings, bytes_type, numbers, ListItemRemovedOrAdded, notpresent,
                             IndexedHash, Verbose, unprocessed, json_convertor_default, add_to_frozen_set,
                             convert_item_or_items_into_set_else_none, get_type,
                             convert_item_or_items_into_compiled_regexes_else_none, current_dir)
from deepdiff.model import RemapDict, ResultDict, TextResult, TreeResult, DiffLevel
from deepdiff.model import DictRelationship, AttributeRelationship
from deepdiff.model import SubscriptableIterableRelationship, NonSubscriptableIterableRelationship, SetRelationship
from deepdiff.deephash import DeepHash
from deepdiff.base import Base

logger = logging.getLogger(__name__)
warnings.simplefilter('once', DeprecationWarning)

TREE_VIEW = 'tree'
TEXT_VIEW = 'text'

with open(os.path.join(current_dir, 'diff_doc.rst'), 'r') as doc_file:
    doc = doc_file.read()


class DeepDiff(ResultDict, Base):
    __doc__ = doc

    def __init__(self,
                 t1,
                 t2,
                 ignore_order=False,
                 report_repetition=False,
                 significant_digits=None,
                 exclude_paths=None,
                 exclude_regex_paths=None,
                 exclude_types=None,
                 ignore_type_in_groups=None,
                 ignore_string_type_changes=False,
                 ignore_numeric_type_changes=False,
                 verbose_level=1,
                 view=TEXT_VIEW,
                 hasher=None,
                 **kwargs):
        if kwargs:
            raise ValueError((
                "The following parameter(s) are not valid: %s\n"
                "The valid parameters are ignore_order, report_repetition, significant_digits, "
                "exclude_paths, exclude_types, exclude_regex_paths, ignore_type_in_groups, "
                "ignore_string_type_changes, ignore_numeric_type_changes, verbose_level, view, "
                "and hasher.") % ', '.join(kwargs.keys()))

        self.ignore_order = ignore_order
        self.ignore_type_in_groups = self.get_ignore_types_in_groups(
            ignore_type_in_groups,
            ignore_string_type_changes, ignore_numeric_type_changes)
        self.report_repetition = report_repetition
        self.exclude_paths = convert_item_or_items_into_set_else_none(exclude_paths)
        self.exclude_regex_paths = convert_item_or_items_into_compiled_regexes_else_none(exclude_regex_paths)
        self.exclude_types = set(exclude_types) if exclude_types else None
        self.exclude_types_tuple = tuple(exclude_types) if exclude_types else None  # we need tuple for checking isinstance
        self.ignore_string_type_changes = ignore_string_type_changes
        self.ignore_numeric_type_changes = ignore_numeric_type_changes
        self.hashes = {}
        self.hasher = hasher

        self.significant_digits = self.get_significant_digits(significant_digits, ignore_numeric_type_changes)

        self.tree = TreeResult()

        Verbose.level = verbose_level

        root = DiffLevel(t1, t2)
        self.__diff(root, parents_ids=frozenset({id(t1)}))

        self.tree.cleanup()

        self.view = view
        view_results = self._get_view_results(view)
        self.update(view_results)

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
        else:
            if self.exclude_types_tuple and (isinstance(level.t1, self.exclude_types_tuple) or
                                             isinstance(level.t2, self.exclude_types_tuple)):
                skip = True

        return skip

    def __get_clean_to_keys_mapping(self, keys, level):
        result = {}
        for key in keys:
            if self.ignore_string_type_changes and isinstance(key, bytes):
                clean_key = key.decode('utf-8')
            elif self.ignore_numeric_type_changes and type(key) in numbers:
                clean_key = ("{:.%sf}" % self.significant_digits).format(key)
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
            key = t2_clean_to_keys[key] if t2_clean_to_keys else key
            change_level = level.branch_deeper(
                notpresent,
                t2[key],
                child_relationship_class=rel_class,
                child_relationship_param=key)
            self.__report_result(item_added_key, change_level)

        for key in t_keys_removed:
            key = t1_clean_to_keys[key] if t1_clean_to_keys else key
            change_level = level.branch_deeper(
                t1[key],
                notpresent,
                child_relationship_class=rel_class,
                child_relationship_param=key)
            self.__report_result(item_removed_key, change_level)

        for key in t_keys_intersect:  # key present in both dicts - need to compare values
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
                                      exclude_paths=self.exclude_paths,
                                      exclude_regex_paths=self.exclude_regex_paths,
                                      hasher=self.hasher,
                                      ignore_repetition=not self.report_repetition,
                                      significant_digits=self.significant_digits,
                                      ignore_string_type_changes=self.ignore_string_type_changes,
                                      ignore_numeric_type_changes=self.ignore_numeric_type_changes,
                                      ignore_type_in_groups=self.ignore_type_in_groups,
                                      )
                item_hash = hashes_all[item]
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

        if get_type(level.t1) != get_type(level.t2):
            report_type_change = True
            for type_group in self.ignore_type_in_groups:
                if get_type(level.t1) in type_group and get_type(level.t2) in type_group:
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
        Get the json pickle of the diff object. Unless you need all the attributes and functionality of DeepDiff, running to_json() is the safer option that json pickle.
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
        Dump json of the text view.
        **Parameters**

        default_mapping : default_mapping, dictionary(optional), a dictionary of mapping of different types to json types.

        by default DeepDiff converts certain data types. For example Decimals into floats so they can be exported into json.
        If you have a certain object type that the json serializer can not serialize it, please pass the appropriate type
        conversion through this dictionary.

        **Example**

        Serialize custom objects
            >>> class A:
            ...     pass
            ...
            >>> class B:
            ...     pass
            ...
            >>> t1 = A()
            >>> t2 = B()
            >>> ddiff = DeepDiff(t1, t2)
            >>> ddiff.to_json()
            TypeError: We do not know how to convert <__main__.A object at 0x10648> of type <class '__main__.A'> for json serialization. Please pass the default_mapping parameter with proper mapping of the object to a basic python type.

            >>> default_mapping = {A: lambda x: 'obj A', B: lambda x: 'obj B'}
            >>> ddiff.to_json(default_mapping=default_mapping)
            '{"type_changes": {"root": {"old_type": "A", "new_type": "B", "old_value": "obj A", "new_value": "obj B"}}}'
        """
        return json.dumps(self.to_dict(), default=json_convertor_default(default_mapping=default_mapping))

    def to_dict(self):
        """
        Dump dictionary of the text view. It does not matter which view you are currently in. It will give you the dictionary of the text view.
        """
        if self.view == TREE_VIEW:
            result = dict(self._get_view_results(view=TEXT_VIEW))
        else:
            result = dict(self)
        return result


if __name__ == "__main__":  # pragma: no cover
    import doctest
    doctest.testmod()
