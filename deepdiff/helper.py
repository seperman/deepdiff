# -*- coding: utf-8 -*-

import sys
import datetime
from decimal import Decimal
from collections import namedtuple
from collections import MutableMapping
from collections import Iterable
import logging

py_major_version = sys.version[0]
py_minor_version = sys.version[2]

py3 = py_major_version == '3'

if (py_major_version, py_minor_version) == (2.6):  # pragma: no cover
    sys.exit('Python 2.6 is not supported.')

if py3:  # pragma: no cover
    from builtins import int

    strings = (str, bytes)  # which are both basestring
    numbers = (int, float, complex, datetime.datetime, datetime.date, Decimal)

    items = 'items'
else:  # pragma: no cover
    strings = (str, unicode)
    numbers = (int, float, long, complex, datetime.datetime, datetime.date, Decimal)

    items = 'iteritems'

IndexedHash = namedtuple('IndexedHash', 'indexes item')

EXPANDED_KEY_MAP = {  # pragma: no cover
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


def order_unordered(data):
    """
    Order unordered data.

    We use it in pickling so that serializations are consistent
    since pickle serializes data inconsistently for unordered iterables
    such as dictionary and set.
    """
    if isinstance(data, MutableMapping):
        data = sorted(data.items(), key=lambda x: x[0])
        for i, item in enumerate(data):
            data[i] = (item[0], order_unordered(item[1]))
    elif isinstance(data, Iterable) and not isinstance(data, strings):
        try:
            data = sorted(data)
        except Exception as e:
            warn("Unable to order data type: %s. "
                 "Ignore order might be giving inaccurate results.",
                 type(data), exc_info=True)
        else:
            new_data = []
            for item in data:
                item = order_unordered(item)
                new_data.append(item)
            data = new_data

    return data


def is_string(param):
    if py3:
        return isinstance(param, str)
    else:
        return isinstance(param, basestring)


class ListItemRemovedOrAdded(object):  # pragma: no cover

    """Class of conditions to be checked"""

    pass

INDEX_VS_ATTRIBUTE = ('[%s]', '.%s')


logging.basicConfig(format='%(asctime)s %(levelname)8s %(message)s')
logger = logging.getLogger()

WARNING_NUM = 0

def warn(*args, **kwargs):
    global WARNING_NUM

    if WARNING_NUM < 10:
        WARNING_NUM += 1
        logger.warning(*args, **kwargs)


class RemapDict(dict):
    """
    Remap Dictionary.

    For keys that have a new, longer name, remap the old key to the new key.
    Other keys that don't have a new name are handled as before.
    """

    def __getitem__(self, old_key):
        new_key = EXPANDED_KEY_MAP.get(old_key, old_key)
        if new_key != old_key:
            warn("DeepDiff Deprecation: %s is renamed to %s. Please start using "
                 "the new unified naming convention.", old_key, new_key)
        if new_key in self:
            return self.get(new_key)
        else:  # pragma: no cover
            raise KeyError(new_key)
