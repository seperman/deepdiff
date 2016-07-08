# -*- coding: utf-8 -*-

from __future__ import print_function

from collections import namedtuple
from collections import MutableMapping
import sys
import datetime
from decimal import Decimal


IndexedHash = namedtuple('IndexedHash', 'indexes item')

EXPANDED_KEY_MAP = {
    'dic_item_added': 'dictionary_item_added',
    'dic_item_removed': 'dictionary_item_removed',
    'newindexes': 'new_indexes',
    'newrepeat': 'new_repeat',
    'newtype': 'new_type',
    'newvalue': 'new_value',
    'oldindexes': 'old_indexes',
    'oldrepeat': 'old_repeat',
    'oldtype': 'old_type',
    'oldvalue': 'old_value'}


py_major_version = sys.version[0]
py_minor_version = sys.version[2]

py3 = py_major_version == '3'

if (py_major_version, py_minor_version) == (2.6):
    sys.exit('Python 2.6 is not supported.')

if py3:
    from builtins import int
    strings = (str, bytes)  # which are both basestring
    numbers = (int, float, complex, datetime.datetime, Decimal)
    from itertools import zip_longest
    # from _string import formatter_field_name_split
    items = 'items'
else:
    strings = (str, unicode)
    numbers = (int, float, long, complex, datetime.datetime, Decimal)
    from itertools import izip_longest as zip_longest
    items = 'iteritems'
    # formatter_field_name_split = str._formatter_field_name_split


def eprint(*args, **kwargs):
    """print to stdout written by @MarcH"""
    print(*args, file=sys.stderr, **kwargs)


def order_unordered(data):
    """
    orders unordered data.
    We use it in pickling so that serializations are consistent
    since pickle serializes data inconsistently for unordered iterables
    such as dictionary and set.
    """
    if isinstance(data, MutableMapping):
        data = sorted(data.items(), key=lambda x: x[0])
        for i, item in enumerate(data):
            data[i] = (item[0], order_unordered(item[1]))
    elif isinstance(data, (set, frozenset)):
        data = sorted(data)

    return data


class ListItemRemovedOrAdded(object):

    """Class of conditions to be checked"""

    pass

INDEX_VS_ATTRIBUTE = ('[%s]', '.%s')


class RemapDict(dict):
    """
    For keys that have a new, longer name, remap the old key to the new key.
    Other keys that don't have a new name are handled as before.
    """

    def __getitem__(self, old_key):
        new_key = EXPANDED_KEY_MAP.get(old_key, old_key)
        return self.get(new_key)

