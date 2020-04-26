import sys
import datetime
import re
import os
import logging
import warnings
from decimal import Decimal, localcontext
from collections import namedtuple
from collections.abc import Mapping, Iterable
from ordered_set import OrderedSet


class np_type:
    pass


try:
    import numpy as np
except ImportError:
    np_ndarray = np_bool_ = np_int32 = np_type
else:
    np_ndarray = np.ndarray
    np_bool_ = np.bool_
    np_int32 = np.int32

logger = logging.getLogger(__name__)

py_major_version = sys.version_info.major
py_minor_version = sys.version_info.minor

py_current_version = Decimal("{}.{}".format(py_major_version, py_minor_version))

py2 = py_major_version == 2
py3 = py_major_version == 3
py4 = py_major_version == 4

MINIMUM_PY_DICT_TYPE_SORTED = Decimal('3.6')
DICT_IS_SORTED = py_current_version >= MINIMUM_PY_DICT_TYPE_SORTED

if py4:
    logger.warning('Python 4 is not supported yet. Switching logic to Python 3.')  # pragma: no cover
    py3 = True  # pragma: no cover

if py2:  # pragma: no cover
    sys.exit('Python 2 is not supported anymore. The last version of DeepDiff that supported Py2 was 3.3.0')

pypy3 = py3 and hasattr(sys, "pypy_translation_info")

strings = (str, bytes)  # which are both basestring
unicode_type = str
bytes_type = bytes
numbers = (int, float, complex, datetime.datetime, datetime.date,
           datetime.timedelta, Decimal, datetime.time, np_int32)
booleans = (bool, np_bool_)

IndexedHash = namedtuple('IndexedHash', 'indexes item')

current_dir = os.path.dirname(os.path.abspath(__file__))

ID_PREFIX = '!>*id'

ZERO_DECIMAL_CHARACTERS = set("-0.")

KEY_TO_VAL_STR = "{}:{}"


def short_repr(item, max_length=15):
    """Short representation of item if it is too long"""
    item = repr(item)
    if len(item) > max_length:
        item = '{}...{}'.format(item[:max_length - 3], item[-1])
    return item


class ListItemRemovedOrAdded:  # pragma: no cover
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


class NotPresent:  # pragma: no cover
    """
    In a change tree, this indicated that a previously existing object has been removed -- or will only be added
    in the future.
    We previously used None for this but this caused problem when users actually added and removed None. Srsly guys? :D
    """
    def __repr__(self):
        return 'not present'  # pragma: no cover

    __str__ = __repr__


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


class indexed_set(set):
    """
    A set class that lets you get an item by index

    >>> a = indexed_set()
    >>> a.add(10)
    >>> a.add(20)
    >>> a[0]
    10
    """


JSON_CONVERTOR = {
    Decimal: float,
    OrderedSet: list,
    type: lambda x: x.__name__,
    bytes: lambda x: x.decode('utf-8')
}


def json_convertor_default(default_mapping=None):
    _convertor_mapping = JSON_CONVERTOR.copy()
    if default_mapping:
        _convertor_mapping.update(default_mapping)

    def _convertor(obj):
        for original_type, convert_to in _convertor_mapping.items():
            if isinstance(obj, original_type):
                return convert_to(obj)
        raise TypeError('We do not know how to convert {} of type {} for json serialization. Please pass the default_mapping parameter with proper mapping of the object to a basic python type.'.format(obj, type(obj)))

    return _convertor


def add_to_frozen_set(parents_ids, item_id):
    return parents_ids | {item_id}


def convert_item_or_items_into_set_else_none(items):
    if items:
        if isinstance(items, strings):
            items = {items}
        else:
            items = set(items)
    else:
        items = None
    return items


RE_COMPILED_TYPE = type(re.compile(''))


def convert_item_or_items_into_compiled_regexes_else_none(items):
    if items:
        if isinstance(items, (strings, RE_COMPILED_TYPE)):
            items = [items]
        items = [i if isinstance(i, RE_COMPILED_TYPE) else re.compile(i) for i in items]
    else:
        items = None
    return items


def get_id(obj):
    """
    Adding some characters to id so they are not just integers to reduce the risk of collision.
    """
    return "{}{}".format(ID_PREFIX, id(obj))


def get_type(obj):
    """
    Get the type of object or if it is a class, return the class itself.
    """
    return obj if type(obj) is type else type(obj)


def type_in_type_group(item, type_group):
    return get_type(item) in type_group


def type_is_subclass_of_type_group(item, type_group):
    return isinstance(item, type_group) or issubclass(item, type_group) or type_in_type_group(item, type_group)


def get_doc(doc_filename):
    try:
        with open(os.path.join(current_dir, doc_filename), 'r') as doc_file:
            doc = doc_file.read()
    except Exception:  # pragma: no cover
        doc = 'Failed to load the docstrings. Please visit: https://github.com/seperman/deepdiff'  # pragma: no cover
    return doc


number_formatting = {
    "f": r'{:.%sf}',
    "e": r'{:.%se}',
}


def number_to_string(number, significant_digits, number_format_notation="f"):
    """
    Convert numbers to string considering significant digits.
    """
    try:
        using = number_formatting[number_format_notation]
    except KeyError:
        raise ValueError("number_format_notation got invalid value of {}. The valid values are 'f' and 'e'".format(number_format_notation)) from None
    if isinstance(number, Decimal):
        tup = number.as_tuple()
        with localcontext() as ctx:
            ctx.prec = len(tup.digits) + tup.exponent + significant_digits
            number = number.quantize(Decimal('0.' + '0' * significant_digits))
    result = (using % significant_digits).format(number)
    # Special case for 0: "-0.00" should compare equal to "0.00"
    if set(result) <= ZERO_DECIMAL_CHARACTERS:
        result = "0.00"
    # https://bugs.python.org/issue36622
    if number_format_notation == 'e' and isinstance(number, float):
        result = result.replace('+0', '+')
    return result


class DeepDiffDeprecationWarning(DeprecationWarning):
    """
    Use this warning instead of DeprecationWarning
    """
    pass


def get_diff_length(item):
    """
    Get the number of operations in a diff object.
    It is designed mainly for the delta view output
    but can be used with other dictionary types of view outputs too.
    """
    length = 0
    if hasattr(item, '_diff_length'):
        length = item._diff_length
    elif isinstance(item, Mapping):
        for key, subitem in item.items():
            length += get_diff_length(subitem)
    elif isinstance(item, numbers):
        length = 1
    elif isinstance(item, strings):
        length = 1
    elif isinstance(item, Iterable):
        for subitem in item:
            length += get_diff_length(subitem)
    elif isinstance(item, type):  # it is a class
        length = 1
    else:
        if hasattr(item, '__dict__'):
            for subitem in item.__dict__:
                length += get_diff_length(subitem)

    try:
        item._diff_length = length
    except Exception:
        pass
    return length


def cartesian_product(a, b):
    """
    Get the Cartesian product of two iterables

    **parameters**

    a: list of lists
    b: iterable to do the Cartesian product
    """

    for i in a:
        for j in b:
            yield i + (j,)


def cartesian_product_of_shape(dimentions, result=None):
    """
    Cartesian product of a dimentions iterable.
    This is mainly used to traverse Numpy ndarrays.

    Each array has dimentions that are defines in ndarray.shape
    """
    if result is None:
        result = ((),)  # a tuple with an empty tuple
    for dimension in dimentions:
        result = cartesian_product(result, range(dimension))
    return result


def get_numpy_ndarray_rows(obj):
    """
    Convert a multi dimensional numpy array to list of rows
    """
    dimentions = obj.shape[:-1]
    for path in cartesian_product_of_shape(dimentions):
        result = obj
        for index in path:
            result = result[index]
        yield path, result


warnings.simplefilter('once', DeepDiffDeprecationWarning)
