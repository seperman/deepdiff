#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
from collections import Iterable
from collections import MutableMapping
from collections import defaultdict
from decimal import Decimal
from hashlib import sha1, sha256

from deepdiff.helper import (strings, numbers, unprocessed, not_hashed, add_to_frozen_set,
                             convert_item_or_items_into_set_else_none, current_dir,
                             convert_item_or_items_into_compiled_regexes_else_none,
                             get_id)
from deepdiff.base import Base
logger = logging.getLogger(__name__)

try:
    import mmh3
except ImportError:
    logger.warning('Can not find Murmur3 hashing installed. Switching to SHA256 as the default hash. Refer to https://github.com/seperman/deepdiff#murmur3 for more info.')
    mmh3 = False

UNPROCESSED = 'unprocessed'
MURMUR_SEED = 1203

RESERVED_DICT_KEYS = {UNPROCESSED}
EMPTY_FROZENSET = frozenset({})

INDEX_VS_ATTRIBUTE = ('[%s]', '.%s')

KEY_TO_VAL_STR = "{}:{}"

ZERO_DECIMAL_CHARACTERS = set("-0.")


def prepare_string_for_hashing(obj, ignore_string_type_changes=False):
    """
    Clean type conversions
    """
    original_type = obj.__class__.__name__
    if isinstance(obj, bytes):
        obj = obj.decode('utf-8')
    if not ignore_string_type_changes:
        obj = KEY_TO_VAL_STR.format(original_type, obj)
    return obj


with open(os.path.join(current_dir, 'deephash_doc.rst'), 'r') as doc_file:
    doc = doc_file.read()


class DeepHash(dict, Base):
    __doc__ = doc

    def __init__(self,
                 obj,
                 *,
                 hashes=None,
                 exclude_types=None,
                 exclude_paths=None,
                 exclude_regex_paths=None,
                 hasher=None,
                 ignore_repetition=True,
                 significant_digits=None,
                 apply_hash=True,
                 ignore_type_in_groups=None,
                 ignore_string_type_changes=False,
                 ignore_numeric_type_changes=False,
                 **kwargs):
        if kwargs:
            raise ValueError(
                ("The following parameter(s) are not valid: %s\n"
                 "The valid parameters are obj, hashes, exclude_types,"
                 "exclude_paths, exclude_regex_paths, hasher, ignore_repetition,"
                 "significant_digits, apply_hash, ignore_type_in_groups, ignore_string_type_changes,"
                 "ignore_numeric_type_changes") % ', '.join(kwargs.keys()))
        self.obj = obj
        exclude_types = set() if exclude_types is None else set(exclude_types)
        self.exclude_types_tuple = tuple(exclude_types)  # we need tuple for checking isinstance
        self.ignore_repetition = ignore_repetition
        self.exclude_paths = convert_item_or_items_into_set_else_none(exclude_paths)
        self.exclude_regex_paths = convert_item_or_items_into_compiled_regexes_else_none(exclude_regex_paths)
        default_hasher = self.murmur3_128bit if mmh3 else self.sha256hex
        self.hasher = default_hasher if hasher is None else hasher
        hashes = hashes if hashes else {}
        self.update(hashes)
        self[UNPROCESSED] = []

        self.significant_digits = self.get_significant_digits(significant_digits, ignore_numeric_type_changes)
        self.ignore_type_in_groups = self.get_ignore_types_in_groups(
            ignore_type_in_groups,
            ignore_string_type_changes, ignore_numeric_type_changes)
        self.ignore_string_type_changes = ignore_string_type_changes
        self.ignore_numeric_type_changes = ignore_numeric_type_changes
        # makes the hash return constant size result if true
        # the only time it should be set to False is when
        # testing the individual hash functions for different types of objects.
        self.apply_hash = apply_hash

        self._hash(obj, parent="root", parents_ids=frozenset({get_id(obj)}))

        if self[UNPROCESSED]:
            logger.warning("Can not hash the following items: {}.".format(self[UNPROCESSED]))
        else:
            del self[UNPROCESSED]

    @staticmethod
    def sha256hex(obj):
        """Use Sha256 as a cryptographic hash."""
        obj = obj.encode('utf-8')
        return sha256(obj).hexdigest()

    @staticmethod
    def sha1hex(obj):
        """Use Sha1 as a cryptographic hash."""
        obj = obj.encode('utf-8')
        return sha1(obj).hexdigest()

    @staticmethod
    def murmur3_64bit(obj):
        """
        Use murmur3_64bit for 64 bit hash by passing this method:
        hasher=DeepHash.murmur3_64bit
        """
        obj = obj.encode('utf-8')
        # This version of murmur3 returns two 64bit integers.
        return mmh3.hash64(obj, MURMUR_SEED)[0]

    @staticmethod
    def murmur3_128bit(obj):
        """
        Use murmur3_128bit for bit hash by passing this method:
        hasher=DeepHash.murmur3_128bit
        This hasher is the default hasher.
        """
        obj = obj.encode('utf-8')
        return mmh3.hash128(obj, MURMUR_SEED)

    def __getitem__(self, obj):
        # changed_to_id = False
        key = obj
        result = None

        try:
            result = super().__getitem__(key)
        except (TypeError, KeyError):
            key = get_id(obj)
            try:
                result = super().__getitem__(key)
            except KeyError:
                raise KeyError('{} is not one of the hashed items.'.format(obj)) from None
        return result

    def __contains__(self, obj):
        try:
            hash(obj)
        except TypeError:
            key = get_id(obj)
        else:
            key = obj
        return super().__contains__(key)

    def _prep_obj(self, obj, parent, parents_ids=EMPTY_FROZENSET, is_namedtuple=False):
        """Difference of 2 objects"""
        original_type = type(obj)
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

        result = self._prep_dict(obj, parent=parent, parents_ids=parents_ids,
                                 print_as_attribute=True, original_type=original_type)
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

    def _prep_dict(self, obj, parent, parents_ids=EMPTY_FROZENSET, print_as_attribute=False, original_type=None):

        result = []

        key_text = "%s{}".format(INDEX_VS_ATTRIBUTE[print_as_attribute])
        for key, item in obj.items():
            key_formatted = "'%s'" % key if not print_as_attribute and isinstance(key, strings) else key
            key_in_report = key_text % (parent, key_formatted)

            key_hash = self._hash(key, parent=key_in_report, parents_ids=parents_ids)
            item_id = get_id(item)
            if (parents_ids and item_id in parents_ids) or self._skip_this(item, parent=key_in_report):
                continue
            parents_ids_added = add_to_frozen_set(parents_ids, item_id)
            hashed = self._hash(item, parent=key_in_report, parents_ids=parents_ids_added)
            hashed = KEY_TO_VAL_STR.format(key_hash, hashed)
            result.append(hashed)

        result.sort()
        result = ';'.join(result)
        if print_as_attribute:
            type_ = original_type or type(obj)
            type_str = type_.__name__
            for type_group in self.ignore_type_in_groups:
                if type_ in type_group:
                    type_str = ','.join(map(lambda x: x.__name__, type_group))
                    break
        else:
            type_str = 'dict'
        return "%s:{%s}" % (type_str, result)

    def _prep_set(self, obj, parent, parents_ids=EMPTY_FROZENSET):
        return "set:{}".format(self._prep_iterable(obj=obj, parent=parent, parents_ids=parents_ids))

    def _prep_iterable(self, obj, parent, parents_ids=EMPTY_FROZENSET):

        result = defaultdict(int)

        for i, item in enumerate(obj):
            if self._skip_this(item, parent="{}[{}]".format(parent, i)):
                continue

            item_id = get_id(item)
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
        result = KEY_TO_VAL_STR.format(type(obj).__name__, result)

        return result

    def _prep_number(self, obj):
        if self.significant_digits is not None and (
                self.ignore_numeric_type_changes or isinstance(obj, (float, complex, Decimal))):
            obj_s = ("{:.%sf}" % self.significant_digits).format(obj)

            # Special case for 0: "-0.00" should compare equal to "0.00"
            if set(obj_s) <= ZERO_DECIMAL_CHARACTERS:
                obj_s = "0.00"
            result = "number:{}".format(obj_s)
        else:
            result = KEY_TO_VAL_STR.format(type(obj).__name__, obj)
        return result

    def _prep_tuple(self, obj, parent, parents_ids):
        # Checking to see if it has _fields. Which probably means it is a named
        # tuple.
        try:
            obj._asdict
        # It must be a normal tuple
        except AttributeError:
            result = self._prep_iterable(obj=obj, parent=parent, parents_ids=parents_ids)
        # We assume it is a namedtuple then
        else:
            result = self._prep_obj(obj, parent, parents_ids=parents_ids, is_namedtuple=True)
        return result

    def _hash(self, obj, parent, parents_ids=EMPTY_FROZENSET):
        """The main diff method"""

        try:
            result = self[obj]
        except (TypeError, KeyError):
            pass
        else:
            return result

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
            result = self._prep_dict(obj=obj, parent=parent, parents_ids=parents_ids)

        elif isinstance(obj, tuple):
            result = self._prep_tuple(obj=obj, parent=parent, parents_ids=parents_ids)

        elif isinstance(obj, (set, frozenset)):
            result = self._prep_set(obj=obj, parent=parent, parents_ids=parents_ids)

        elif isinstance(obj, Iterable):
            result = self._prep_iterable(obj=obj, parent=parent, parents_ids=parents_ids)

        else:
            result = self._prep_obj(obj=obj, parent=parent, parents_ids=parents_ids)

        if result is not_hashed:  # pragma: no cover
            self[UNPROCESSED].append(obj)

        elif result is unprocessed:
            pass

        elif self.apply_hash:
            if isinstance(obj, strings):
                result_cleaned = result
            else:
                result_cleaned = prepare_string_for_hashing(result, ignore_string_type_changes=self.ignore_string_type_changes)
            result = self.hasher(result_cleaned)

        # It is important to keep the hash of all objects.
        # The hashes will be later used for comparing the objects.
        try:
            self[obj] = result
        except TypeError:
            obj_id = get_id(obj)
            self[obj_id] = result

        return result


if __name__ == "__main__":  # pragma: no cover
    import doctest
    doctest.testmod()
