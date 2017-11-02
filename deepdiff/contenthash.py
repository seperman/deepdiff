#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
import sys
from collections import Iterable
from collections import MutableMapping
from collections import defaultdict
from decimal import Decimal
from hashlib import sha1
import logging

from deepdiff.helper import py3, int, strings, numbers, items

logger = logging.getLogger(__name__)


class Skipped(object):
    def __repr__(self):
        return "Skipped"  # pragma: no cover

    def __str__(self):
        return "Skipped"  # pragma: no cover


class Unprocessed(object):
    def __repr__(self):
        return "Error: Unprocessed"  # pragma: no cover

    def __str__(self):
        return "Error: Unprocessed"  # pragma: no cover


class NotHashed(object):
    def __repr__(self):
        return "Error: NotHashed"  # pragma: no cover

    def __str__(self):
        return "Error: NotHashed"  # pragma: no cover


class DeepHash(dict):
    r"""
    **DeepHash**

    DeepHash calculates the hash of objects based on their contents in a deterministic way.
    This way 2 objects with the same content should have the same hash.

    The main usage of DeepHash is to calculate the hash of otherwise unhashable objects.
    For example you can use DeepHash to calculate the hash of a set or a dictionary!

    The core of DeepHash is a deterministic serialization of your object into a string so it
    can be passed to a hash function. By default it uses Python's built-in hash function
    but you can pass another hash function to it if you want.
    For example the Murmur3 hash function or a cryptographic hash function.


    **Parameters**

    obj : any object, The object to be hashed based on its content.

    hashes : dictionary, default = empty dictionary.
        A dictionary of {object id: object hash} to start with.
        Any object that is encountered and its id is already in the hashes dictionary,
        will re-use the hash that is provided by this dictionary instead of re-calculating
        its hash.

    exclude_types: list, default = None.
        List of object types to exclude from hashing.
        Note that the deepdiff diffing functionality lets this to be the default at all times.
        But if you are using DeepHash directly, you can set this parameter.

    hasher: function. default = hash
        hasher is the hashing function. The default is built-in hash function.
        But you can pass another hash function to it if you want.
        For example the Murmur3 hash function or a cryptographic hash function.
        All it needs is a function that takes the input in string format
        and return the hash.

        SHA1 is already provided as an alternative to the built-in hash function.
        You can use it by passing: hasher=DeepHash.sha1hex

    ignore_repetition: Boolean, default = True
        If repetitions in an iterable should cause the hash of iterable to be different.
        Note that the deepdiff diffing functionality lets this to be the default at all times.
        But if you are using DeepHash directly, you can set this parameter.

    significant_digits : int >= 0, default=None.
        If it is a non negative integer, it compares only that many digits AFTER
        the decimal point.

        This only affects floats, decimal.Decimal and complex.

        Takse a look at DeepDiff.diff docs for explanation of how this works.

    constant_size: Boolean, default = True
        What DeepHash does is to "prep" the contents of objects into strings.
        If constant_size is set, then it actually goes ahead and hashes the string
        using the hasher function.

        The only time you want the constant_size to be False is if you want to know what
        the string representation of your object is BEFORE it gets hashed.

    **Returns**
        A dictionary of {item id: item hash}.
        If your object is nested, it will include hashes of all the objects it includes!


    **Examples**

    Let's say you have a dictionary object.
        >>> from deepdiff import DeepHash
        >>>
        >>> obj = {1: 2, 'a': 'b'}

    If you try to hash itL
        >>> hash(obj)
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        TypeError: unhashable type: 'dict'

    But with DeepHash:

    """

    def __init__(self,
                 obj,
                 hashes=None,
                 exclude_types=set(),
                 hasher=None,
                 ignore_repetition=True,
                 significant_digits=None,
                 constant_size=True,
                 **kwargs):
        if kwargs:
            raise ValueError(
                ("The following parameter(s) are not valid: %s\n"
                 "The valid parameters are obj, hashes, exclude_types."
                 "hasher and ignore_repetition.") % ', '.join(kwargs.keys()))
        self.obj = obj
        self.exclude_types = set(exclude_types)
        self.exclude_types_tuple = tuple(
            exclude_types)  # we need tuple for checking isinstance
        self.ignore_repetition = ignore_repetition

        self.hasher = hash if hasher is None else hasher
        hashes = hashes if hashes else {}
        self.update(hashes)
        self['unprocessed'] = []
        self.unprocessed = Unprocessed()
        self.skipped = Skipped()
        self.not_hashed = NotHashed()
        self.significant_digits = significant_digits
        # makes the hash return constant size result if true
        # the only time it should be set to False is when
        # testing the individual hash functions for different types of objects.
        self.constant_size = constant_size

        self.__hash(obj, parents_ids=frozenset({id(obj)}))

        if self['unprocessed']:
            logger.warning("Can not hash the following items: {}.".format(self['unprocessed']))
        else:
            del self['unprocessed']

    @staticmethod
    def sha1hex(obj):
        """Use Sha1 for more accuracy."""
        if py3:  # pragma: no cover
            if isinstance(obj, str):
                obj = "{}:{}".format(type(obj).__name__, obj)
                obj = obj.encode('utf-8')
            elif isinstance(obj, bytes):
                obj = type(obj).__name__.encode('utf-8') + b":" + obj
        else:  # pragma: no cover
            if isinstance(obj, unicode):
                obj = u"{}:{}".format(type(obj).__name__, obj)
                obj = obj.encode('utf-8')
            elif isinstance(obj, str):
                obj = type(obj).__name__ + ":" + obj
        return sha1(obj).hexdigest()

    @staticmethod
    def __add_to_frozen_set(parents_ids, item_id):
        parents_ids = set(parents_ids)
        parents_ids.add(item_id)
        return frozenset(parents_ids)

    def __prep_obj(self, obj, parents_ids=frozenset({}), is_namedtuple=False):
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
                self['unprocessed'].append(obj)
                return self.unprocessed

        result = self.__prep_dict(obj, parents_ids)
        result = "nt{}".format(result) if is_namedtuple else "obj{}".format(
            result)
        return result

    def __skip_this(self, obj):
        skip = False
        if isinstance(obj, self.exclude_types_tuple):
            skip = True

        return skip

    def __prep_dict(self, obj, parents_ids=frozenset({})):

        result = []
        obj_keys = set(obj.keys())

        for key in obj_keys:
            key_hash = self.__hash(key)
            item = obj[key]
            item_id = id(item)
            if parents_ids and item_id in parents_ids:
                continue
            parents_ids_added = self.__add_to_frozen_set(parents_ids, item_id)
            hashed = self.__hash(item, parents_ids_added)
            hashed = "{}:{}".format(key_hash, hashed)
            result.append(hashed)

        result.sort()
        result = ';'.join(result)
        result = "dict:{%s}" % result

        return result

    def __prep_set(self, obj):
        return "set:{}".format(self.__prep_iterable(obj))

    def __prep_iterable(self, obj, parents_ids=frozenset({})):

        result = defaultdict(int)

        for i, x in enumerate(obj):
            if self.__skip_this(x):
                continue

            item_id = id(x)
            if parents_ids and item_id in parents_ids:
                continue

            parents_ids_added = self.__add_to_frozen_set(parents_ids, item_id)
            hashed = self.__hash(x, parents_ids_added)
            # counting repetitions
            result[hashed] += 1

        if self.ignore_repetition:
            result = list(result.keys())
        else:
            # items could be iteritems based on py version so we use getattr
            result = [
                '{}|{}'.format(i, v) for i, v in getattr(result, items)()
            ]

        result.sort()
        result = map(str, result)  # making sure the result items are string so join command works.
        result = ','.join(result)
        result = "{}:{}".format(type(obj).__name__, result)

        return result

    def __prep_str(self, obj):
        return 'str:{}'.format(obj)

    def __prep_number(self, obj):
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

    def __prep_tuple(self, obj, parents_ids):
        # Checking to see if it has _fields. Which probably means it is a named
        # tuple.
        try:
            obj._asdict
        # It must be a normal tuple
        except AttributeError:
            result = self.__prep_iterable(obj, parents_ids)
        # We assume it is a namedtuple then
        else:
            result = self.__prep_obj(obj, parents_ids, is_namedtuple=True)
        return result

    def __hash(self, obj, parents_ids=frozenset({})):
        """The main diff method"""

        obj_id = id(obj)
        if obj_id in self:
            return self[obj_id]

        result = self.not_hashed

        if self.__skip_this(obj):
            result = self.skipped

        elif obj is None:
            result = 'NONE'

        elif isinstance(obj, strings):
            result = self.__prep_str(obj)

        elif isinstance(obj, numbers):
            result = self.__prep_number(obj)

        elif isinstance(obj, MutableMapping):
            result = self.__prep_dict(obj, parents_ids)

        elif isinstance(obj, tuple):
            result = self.__prep_tuple(obj, parents_ids)

        elif isinstance(obj, (set, frozenset)):
            result = self.__prep_set(obj)

        elif isinstance(obj, Iterable):
            result = self.__prep_iterable(obj, parents_ids)

        else:
            result = self.__prep_obj(obj, parents_ids)

        if result is self.not_hashed:  # pragma: no cover
            self['unprocessed'].append(obj)

        elif self.constant_size:
            result = self.hasher(result)

        # It is important to keep the hash of all objects.
        # The hashes will be later used for comparing the objects.
        self[obj_id] = result

        return result


if __name__ == "__main__":  # pragma: no cover
    if not py3:
        sys.exit("Please run with Python 3 to verify the doc strings.")
    import doctest
    doctest.testmod()
