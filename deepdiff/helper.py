# -*- coding: utf-8 -*-
import sys
import datetime
from decimal import Decimal
from collections import namedtuple
import logging

logger = logging.getLogger(__name__)

py_major_version = sys.version[0]
py_minor_version = sys.version[2]

py2 = py_major_version == '2'
py3 = py_major_version == '3'
py4 = py_major_version == '4'

if py4:
    logger.warning('Python 4 is not supported yet. Switching logic to Python 3.')
    py3 = True

if py2:  # pragma: no cover
    sys.exit('Python 2 is not supported anymore. The last version of DeepDiff that supported Py2 was 3.3.0')

pypy3 = py3 and hasattr(sys, "pypy_translation_info")

# from builtins import int
strings = (str, bytes)  # which are both basestring
unicode_type = str
bytes_type = bytes
numbers = (int, float, complex, datetime.datetime, datetime.date, datetime.timedelta, Decimal)

IndexedHash = namedtuple('IndexedHash', 'indexes item')


def short_repr(item, max_length=15):
    """Short representation of item if it is too long"""
    item = repr(item)
    if len(item) > max_length:
        item = '{}...{}'.format(item[:max_length - 3], item[-1])
    return item


class ListItemRemovedOrAdded(object):  # pragma: no cover
    """Class of conditions to be checked"""
    pass


class OtherTypes:
    def __repr__(self):
        return "Error: {}".format(self.__class__.__name__)  # pragma: no cover

    __str__ = __repr__


class Skipped(OtherTypes):
    pass


class Unprocessed(OtherTypes):
    pass


class NotHashed(OtherTypes):
    pass


class NotPresent(OtherTypes):  # pragma: no cover
    """
    In a change tree, this indicated that a previously existing object has been removed -- or will only be added
    in the future.
    We previously used None for this but this caused problem when users actually added and removed None. Srsly guys? :D
    """
    pass


unprocessed = Unprocessed()
skipped = Skipped()
not_hashed = NotHashed()
notpresent = NotPresent()


# Disabling remapping from old to new keys since the mapping is deprecated.
RemapDict = dict


# class RemapDict(dict):
#     """
#     DISABLED
#     Remap Dictionary.

#     For keys that have a new, longer name, remap the old key to the new key.
#     Other keys that don't have a new name are handled as before.
#     """

#     def __getitem__(self, old_key):
#         new_key = EXPANDED_KEY_MAP.get(old_key, old_key)
#         if new_key != old_key:
#             logger.warning(
#                 "DeepDiff Deprecation: %s is renamed to %s. Please start using "
#                 "the new unified naming convention.", old_key, new_key)
#         if new_key in self:
#             return self.get(new_key)
#         else:  # pragma: no cover
#             raise KeyError(new_key)


class Verbose(object):
    """
    Global verbose level
    """
    level = 1
