#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import Iterable
from collections import MutableMapping
from collections import defaultdict
from decimal import Decimal
from hashlib import sha1
import mmh3
import logging

from deepdiff.helper import strings, numbers, unprocessed, skipped, not_hashed

logger = logging.getLogger(__name__)

UNPROCESSED = 'unprocessed'
RESERVED_DICT_KEYS = {UNPROCESSED}


def prepare_string_for_hashing(obj, include_string_type_changes=False):
    """
    Clean type conversions
    """
    original_type = obj.__class__.__name__
    if isinstance(obj, bytes):
        obj = obj.decode('utf-8')
    if include_string_type_changes:
        obj = "{}:{}".format(original_type, obj)
    return obj


class DeepHash(dict):
    r"""
    **DeepHash**

    DeepHash calculates the hash of objects based on their contents in a deterministic way.
    This way 2 objects with the same content should have the same hash.

    The main usage of DeepHash is to calculate the hash of otherwise unhashable objects.
    For example you can use DeepHash to calculate the hash of a set or a dictionary!

    The core of DeepHash is a deterministic serialization of your object into a string so it
    can be passed to a hash function. By default it uses Murmur 3 128 bit hash function.
    but you can pass another hash function to it if you want.

    **Parameters**

    obj : any object, The object to be hashed based on its content.

    hashes : dictionary, default = empty dictionary.
        A dictionary of {object id: object hash} to start with.
        Any object that is encountered and its id is already in the hashes dictionary,
        will re-use the hash that is provided by this dictionary instead of re-calculating
        its hash.

    exclude_types: list, default = None.
        List of object types to exclude from hashing.

    hasher: function. default = DeepHash.murmur3_128bit
        hasher is the hashing function. The default is DeepHash.murmur3_128bit.
        But you can pass another hash function to it if you want.
        For example a cryptographic hash function or Python's builtin hash function.
        All it needs is a function that takes the input in string format and returns the hash.

        You can use it by passing: hasher=hash for Python's builtin hash.

        SHA1 is already provided as an alternative too:
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

    include_string_type_changes: Boolean, default = False
        string type conversions should not affect the hash output when this is set to False.
        For example "Hello" and b"Hello" should produce the same hash.

    **Returns**
        A dictionary of {item id: item hash}.
        If your object is nested, it will build hashes of all the objects it contains!


    **Examples**

    Let's say you have a dictionary object.
        >>> from deepdiff import DeepHash
        >>>
        >>> obj = {1: 2, 'a': 'b'}

    If you try to hash it:
        >>> hash(obj)
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        TypeError: unhashable type: 'dict'

    But with DeepHash:
        >>> from deepdiff import DeepHash
        >>> obj = {1: 2, 'a': 'b'}
        >>> DeepHash(obj)
        {4355639248: (2468916477072481777, 512283587789292749), 4355639280: (-3578777349255665377, -6377555218122431491), 4358636128: (-8839064797231613815, -1822486391929534118), 4358009664: (8833996863197925870, -419376694314494743), 4357467952: (3415089864575009947, 7987229399128149852)}

    So what is exactly the hash of obj in this case?
    DeepHash is calculating the hash of the obj and any other object that obj contains.
    The output of DeepHash is a dictionary of object IDs to their hashes.
    In order to get the hash of obj itself, you need to use the object (or the id of object) to get its hash:
        >>> hashes = DeepHash(obj)
        >>> hashes[obj]
        (3415089864575009947, 7987229399128149852)

    Which you can write as:
        >>> hashes = DeepHash(obj)[obj]

    At first it might seem weird why DeepHash(obj)[obj] but remember that DeepHash(obj) is a dictionary of hashes of all other objects that obj contains too.

    The result hash is (3415089864575009947, 7987229399128149852).
    In this case the hash of the obj is 128 bit that is divided into 2 64bit integers.
    Using Murmur 3 64bit for hashing is preferred (and is the default behaviour)
    since the chance of hash collision will be minimal and hashing will be deterministic
    and will not depend on the version of the Python.

    If you do a deep copy of obj, it should still give you the same hash:
        >>> from copy import deepcopy
        2481013017017307534
        >>> DeepHash(obj2)[obj2]
        (3415089864575009947, 7987229399128149852)

    Note that by default DeepHash will ignore string type differences. So if your strings were bytes, you would still get the same hash:
        >>> obj3 = {1: 2, b'a': b'b'}
        >>> DeepHash(obj3)[obj3]
        (3415089864575009947, 7987229399128149852)

    But if you want a different hash if string types are different, set include_string_type_changes to True:
        >>> DeepHash(obj3, include_string_type_changes=True)[obj3]
        (6406752576584602448, -8103933101621212760)
    """

    def __init__(self,
                 obj,
                 hashes=None,
                 exclude_types=None,
                 hasher=None,
                 ignore_repetition=True,
                 significant_digits=None,
                 constant_size=True,
                 include_string_type_changes=False,
                 **kwargs):
        if kwargs:
            raise ValueError(
                ("The following parameter(s) are not valid: %s\n"
                 "The valid parameters are obj, hashes, exclude_types."
                 "hasher and ignore_repetition.") % ', '.join(kwargs.keys()))
        self.obj = obj
        exclude_types = set() if exclude_types is None else set(exclude_types)
        self.exclude_types_tuple = tuple(exclude_types)  # we need tuple for checking isinstance
        self.ignore_repetition = ignore_repetition

        self.hasher = self.murmur3_128bit if hasher is None else hasher
        hashes = hashes if hashes else {}
        self.update(hashes)
        self[UNPROCESSED] = []
        self.significant_digits = significant_digits
        self.include_string_type_changes = include_string_type_changes
        # makes the hash return constant size result if true
        # the only time it should be set to False is when
        # testing the individual hash functions for different types of objects.
        self.constant_size = constant_size

        self._hash(obj, parents_ids=frozenset({id(obj)}))

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
        # hash64 is actually 128bit. Weird.
        # 1203 is the seed
        return mmh3.hash64(obj, 1203)

    def __getitem__(self, key):
        if not isinstance(key, int):
            try:
                if key in RESERVED_DICT_KEYS:
                    return super().__getitem__(key)
            except Exception:
                pass
            key = id(key)

        return super().__getitem__(key)

    @staticmethod
    def _add_to_frozen_set(parents_ids, item_id):
        parents_ids = set(parents_ids)
        parents_ids.add(item_id)
        return frozenset(parents_ids)

    def _prep_obj(self, obj, parents_ids=frozenset({}), is_namedtuple=False):
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

        result = self._prep_dict(obj, parents_ids)
        result = "nt{}".format(result) if is_namedtuple else "obj{}".format(result)
        return result

    def _skip_this(self, obj):
        skip = False
        if isinstance(obj, self.exclude_types_tuple):
            skip = True

        return skip

    def _prep_dict(self, obj, parents_ids=frozenset({})):

        result = []

        for key, item in obj.items():
            key_hash = self._hash(key)
            item_id = id(item)
            if (parents_ids and item_id in parents_ids) or self._skip_this(item):
                continue
            parents_ids_added = self._add_to_frozen_set(parents_ids, item_id)
            hashed = self._hash(item, parents_ids_added)
            hashed = "{}:{}".format(key_hash, hashed)
            result.append(hashed)

        result.sort()
        result = ';'.join(result)
        result = "dict:{%s}" % result

        return result

    def _prep_set(self, obj):
        return "set:{}".format(self._prep_iterable(obj))

    def _prep_iterable(self, obj, parents_ids=frozenset({})):

        result = defaultdict(int)

        for item in obj:
            if self._skip_this(item):
                continue

            item_id = id(item)
            if parents_ids and item_id in parents_ids:
                continue

            parents_ids_added = self._add_to_frozen_set(parents_ids, item_id)
            hashed = self._hash(item, parents_ids_added)
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

    def _prep_tuple(self, obj, parents_ids):
        # Checking to see if it has _fields. Which probably means it is a named
        # tuple.
        try:
            obj._asdict
        # It must be a normal tuple
        except AttributeError:
            result = self._prep_iterable(obj, parents_ids)
        # We assume it is a namedtuple then
        else:
            result = self._prep_obj(obj, parents_ids, is_namedtuple=True)
        return result

    def _hash(self, obj, parents_ids=frozenset({})):
        """The main diff method"""

        obj_id = id(obj)
        if obj_id in self:
            return self[obj_id]

        result = not_hashed

        if self._skip_this(obj):
            result = skipped

        elif obj is None:
            result = 'NONE'

        elif isinstance(obj, strings):
            result = prepare_string_for_hashing(obj, include_string_type_changes=self.include_string_type_changes)

        elif isinstance(obj, numbers):
            result = self._prep_number(obj)

        elif isinstance(obj, MutableMapping):
            result = self._prep_dict(obj, parents_ids)

        elif isinstance(obj, tuple):
            result = self._prep_tuple(obj, parents_ids)

        elif isinstance(obj, (set, frozenset)):
            result = self._prep_set(obj)

        elif isinstance(obj, Iterable):
            result = self._prep_iterable(obj, parents_ids)

        else:
            result = self._prep_obj(obj, parents_ids)

        if result is not_hashed:  # pragma: no cover
            self[UNPROCESSED].append(obj)

        elif result is unprocessed:
            pass

        elif self.constant_size:
            if isinstance(obj, strings):
                result_cleaned = result
            else:
                result_cleaned = prepare_string_for_hashing(result, include_string_type_changes=self.include_string_type_changes)
            result = self.hasher(result_cleaned)

        # It is important to keep the hash of all objects.
        # The hashes will be later used for comparing the objects.
        self[obj_id] = result

        return result


if __name__ == "__main__":  # pragma: no cover
    import doctest
    doctest.testmod()
