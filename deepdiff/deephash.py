#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import mmh3
import logging
from collections import Iterable
from collections import MutableMapping
from collections import defaultdict
from decimal import Decimal
from hashlib import sha1

from deepdiff.helper import (strings, numbers, unprocessed, skipped, not_hashed, add_to_frozen_set,
                             convert_item_or_items_into_set_else_none, current_dir,
                             convert_item_or_items_into_compiled_regexes_else_none)

logger = logging.getLogger(__name__)

UNPROCESSED = 'unprocessed'
RESERVED_DICT_KEYS = {UNPROCESSED}
EMPTY_FROZENSET = frozenset({})

INDEX_VS_ATTRIBUTE = ('[%s]', '.%s')


def prepare_string_for_hashing(obj, ignore_string_type_changes=False):
    """
    Clean type conversions
    """
    original_type = obj.__class__.__name__
    if isinstance(obj, bytes):
        obj = obj.decode('utf-8')
    if not ignore_string_type_changes:
        obj = "{}:{}".format(original_type, obj)
    return obj


with open(os.path.join(current_dir, 'deephash_doc.rst'), 'r') as doc_file:
    doc = doc_file.read()


class DeepHash(dict):
    __doc__ = doc

    MURMUR_SEED = 1203

    def __init__(self,
                 obj,
                 hashes=None,
                 exclude_types=None,
                 exclude_paths=None,
                 exclude_regex_paths=None,
                 hasher=None,
                 ignore_repetition=True,
                 significant_digits=None,
                 constant_size=True,
                 ignore_string_type_changes=True,
                 **kwargs):
        if kwargs:
            raise ValueError(
                ("The following parameter(s) are not valid: %s\n"
                 "The valid parameters are obj, hashes, exclude_types,"
                 "exclude_paths, exclude_regex_paths, hasher and ignore_repetition.") % ', '.join(kwargs.keys()))
        self.obj = obj
        exclude_types = set() if exclude_types is None else set(exclude_types)
        self.exclude_types_tuple = tuple(exclude_types)  # we need tuple for checking isinstance
        self.ignore_repetition = ignore_repetition
        self.exclude_paths = convert_item_or_items_into_set_else_none(exclude_paths)
        self.exclude_regex_paths = convert_item_or_items_into_compiled_regexes_else_none(exclude_regex_paths)

        self.hasher = self.murmur3_128bit if hasher is None else hasher
        hashes = hashes if hashes else {}
        self.update(hashes)
        self[UNPROCESSED] = []
        self.significant_digits = significant_digits
        self.ignore_string_type_changes = ignore_string_type_changes
        # makes the hash return constant size result if true
        # the only time it should be set to False is when
        # testing the individual hash functions for different types of objects.
        self.constant_size = constant_size

        self._hash(obj, parent="root", parents_ids=frozenset({id(obj)}))

        if self[UNPROCESSED]:
            logger.warning("Can not hash the following items: {}.".format(self[UNPROCESSED]))
        else:
            del self[UNPROCESSED]

    @staticmethod
    def sha1hex(obj):
        """Use Sha1 as a cryptographic hash."""
        obj = obj.encode('utf-8')
        return sha1(obj).hexdigest()

    @staticmethod
    def murmur3_128bit(obj):
        """Use murmur3_128bit for 128 bit hash (default)."""
        obj = obj.encode('utf-8')
        return mmh3.hash128(obj, DeepHash.MURMUR_SEED)

    def _get_item(self, key, changed_to_id=False):
        try:
            value = super().__getitem__(key)
        except KeyError:
            if changed_to_id:
                raise KeyError('{} is not one of the hashed items.'.format(key)) from None
            else:
                key = id(key)
                value = self._get_item(key, changed_to_id=True)
        else:
            return value

    def __getitem__(self, key):
        changed_to_id = False
        if not isinstance(key, int):
            try:
                if key in RESERVED_DICT_KEYS:
                    return super().__getitem__(key)
            except Exception:
                pass
            key = id(key)
            changed_to_id = True

        return self._get_item(key, changed_to_id=changed_to_id)

    def _prep_obj(self, obj, parent, parents_ids=EMPTY_FROZENSET, is_namedtuple=False):
        """Difference of 2 objects"""
        try:
            if is_namedtuple:
                obj = obj._asdict()
            else:
                obj = obj.__dict__
        except AttributeError:
            try:
                obj = {i: getattr(obj, i) for i in obj.__slots__}
            except AttributeError:
                self[UNPROCESSED].append(obj)
                return unprocessed

        result = self._prep_dict(obj, parent, parents_ids, print_as_attribute=True)
        result = "nt{}".format(result) if is_namedtuple else "obj{}".format(result)
        return result

    def _skip_this(self, obj, parent):
        skip = False
        if self.exclude_paths and parent in self.exclude_paths:
            skip = True
        elif self.exclude_regex_paths and any(
                [exclude_regex_path.search(parent) for exclude_regex_path in self.exclude_regex_paths]):
            skip = True
        else:
            if self.exclude_types_tuple and isinstance(obj, self.exclude_types_tuple):
                skip = True

        return skip

    def _prep_dict(self, obj, parent, parents_ids=EMPTY_FROZENSET, print_as_attribute=False):

        result = []

        key_text = "%s{}".format(INDEX_VS_ATTRIBUTE[print_as_attribute])
        for key, item in obj.items():
            key_formatted = "'%s'" % key if not print_as_attribute and isinstance(key, strings) else key
            key_in_report = key_text % (parent, key_formatted)

            key_hash = self._hash(key, parent=key_in_report, parents_ids=parents_ids)
            item_id = id(item)
            if (parents_ids and item_id in parents_ids) or self._skip_this(item, parent=key_in_report):
                continue
            parents_ids_added = add_to_frozen_set(parents_ids, item_id)
            hashed = self._hash(item, parent=key_in_report, parents_ids=parents_ids_added)
            hashed = "{}:{}".format(key_hash, hashed)
            result.append(hashed)

        result.sort()
        result = ';'.join(result)
        result = "dict:{%s}" % result

        return result

    def _prep_set(self, obj, parent, parents_ids=EMPTY_FROZENSET):
        return "set:{}".format(self._prep_iterable(obj, parent, parents_ids))

    def _prep_iterable(self, obj, parent, parents_ids=EMPTY_FROZENSET):

        result = defaultdict(int)

        for i, item in enumerate(obj):
            if self._skip_this(item, parent="{}[{}]".format(parent, i)):
                continue

            item_id = id(item)
            if parents_ids and item_id in parents_ids:
                continue

            parents_ids_added = add_to_frozen_set(parents_ids, item_id)
            hashed = self._hash(item, parent=parent, parents_ids=parents_ids_added)
            # counting repetitions
            result[hashed] += 1

        if self.ignore_repetition:
            result = list(result.keys())
        else:
            result = [
                '{}|{}'.format(i, v) for i, v in result.items()
            ]

        result = sorted(map(str, result))  # making sure the result items are string and sorted so join command works.
        result = ','.join(result)
        result = "{}:{}".format(type(obj).__name__, result)

        return result

    def _prep_number(self, obj):
        # Based on diff.DeepDiff.__diff_numbers
        if self.significant_digits is not None and isinstance(obj, (
                float, complex, Decimal)):
            obj_s = ("{:.%sf}" % self.significant_digits).format(obj)

            # Special case for 0: "-0.00" should compare equal to "0.00"
            if set(obj_s) <= set("-0."):
                obj_s = "0.00"
            result = "number:{}".format(obj_s)
        else:
            result = "{}:{}".format(type(obj).__name__, obj)
        return result

    def _prep_tuple(self, obj, parent, parents_ids):
        # Checking to see if it has _fields. Which probably means it is a named
        # tuple.
        try:
            obj._asdict
        # It must be a normal tuple
        except AttributeError:
            result = self._prep_iterable(obj, parent, parents_ids)
        # We assume it is a namedtuple then
        else:
            result = self._prep_obj(obj, parent, parents_ids=parents_ids, is_namedtuple=True)
        return result

    def _hash(self, obj, parent, parents_ids=EMPTY_FROZENSET):
        """The main diff method"""

        obj_id = id(obj)
        if obj_id in self:
            return self[obj_id]

        result = not_hashed

        if self._skip_this(obj, parent):
            return

        elif obj is None:
            result = 'NONE'

        elif isinstance(obj, strings):
            result = prepare_string_for_hashing(obj, ignore_string_type_changes=self.ignore_string_type_changes)

        elif isinstance(obj, numbers):
            result = self._prep_number(obj)

        elif isinstance(obj, MutableMapping):
            result = self._prep_dict(obj, parent, parents_ids)

        elif isinstance(obj, tuple):
            result = self._prep_tuple(obj, parent, parents_ids)

        elif isinstance(obj, (set, frozenset)):
            result = self._prep_set(obj, parent, parents_ids)

        elif isinstance(obj, Iterable):
            result = self._prep_iterable(obj, parent, parents_ids)

        else:
            result = self._prep_obj(obj, parent, parents_ids)

        if result is not_hashed:  # pragma: no cover
            self[UNPROCESSED].append(obj)

        elif result is unprocessed:
            pass

        elif self.constant_size:
            if isinstance(obj, strings):
                result_cleaned = result
            else:
                result_cleaned = prepare_string_for_hashing(result, ignore_string_type_changes=self.ignore_string_type_changes)
            result = self.hasher(result_cleaned)

        # It is important to keep the hash of all objects.
        # The hashes will be later used for comparing the objects.
        self[obj_id] = result

        return result


if __name__ == "__main__":  # pragma: no cover
    import doctest
    doctest.testmod()
