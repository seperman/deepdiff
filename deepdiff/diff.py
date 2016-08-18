#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
import sys
import difflib
import datetime
import logging
from decimal import Decimal
from collections import Iterable
from collections import namedtuple
from collections import MutableMapping

from deepdiff.helper import py3
from deepdiff.contenthash import DeepHash

if py3:  # pragma: no cover
    from builtins import int
    strings = (str, bytes)  # which are both basestring
    numbers = (int, float, complex, datetime.datetime, datetime.date, Decimal)
    from itertools import zip_longest
    items = 'items'
else:  # pragma: no cover
    strings = (str, unicode)
    numbers = (int, float, long, complex, datetime.datetime, datetime.date, Decimal)
    from itertools import izip_longest as zip_longest
    items = 'iteritems'

logger = logging.getLogger(__name__)

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


WARNING_NUM = 0


def warn(*args, **kwargs):
    global WARNING_NUM

    if WARNING_NUM < 10:
        WARNING_NUM += 1
        logger.warning(*args, **kwargs)


class ListItemRemovedOrAdded(object):  # pragma: no cover

    """Class of conditions to be checked"""

    pass

INDEX_VS_ATTRIBUTE = ('[%s]', '.%s')


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


class DeepDiff(RemapDict):

    r"""
    **DeepDiff**

    Deep Difference of dictionaries, iterables, strings and almost any other object.
    It will recursively look for all the changes.

    **Parameters**

    t1 : A dictionary, list, string or any python object that has __dict__ or __slots__
        This is the first item to be compared to the second item

    t2 : dictionary, list, string or almost any python object that has __dict__ or __slots__
        The second item is to be compared to the first one

    ignore_order : Boolean, defalt=False ignores orders for iterables.
        Note that if you have iterables contatining any unhashable, ignoring order can be expensive.
        Normally ignore_order does not report duplicates and repetition changes.
        In order to report repetitions, set report_repetition=True in addition to ignore_order=True

    report_repetition : Boolean, default=False reports repetitions when set True
        ONLY when ignore_order is set True too. This works for iterables.
        This feature currently is experimental and is not production ready.

    significant_digits : int >= 0, default=None.
        If it is a non negative integer, it compares only that many digits AFTER
        the decimal point.

        This only affects floats, decimal.Decimal and complex.

        Internally it uses "{:.Xf}".format(Your Number) to compare numbers where X=significant_digits

        Note that "{:.3f}".format(1.1135) = 1.113, but "{:.3f}".format(1.11351) = 1.114

        For Decimals, Python's format rounds 2.5 to 2 and 3.5 to 4 (to the closest even number)

    verbose_level : int >= 0, default = 1.
        Higher verbose level shows you more details.
        For example verbose level 1 shows what dictionary item are added or removed.
        And verbose level 2 shows the value of the items that are added or removed too.

    exclude_paths: list, default = None.
        List of paths to exclude from the report.

    exclude_types: list, default = None.
        List of object types to exclude from the report.


    **Returns**

        A DeepDiff object that has already calculated the difference of the 2 items.

    **Supported data types**

    int, string, unicode, dictionary, list, tuple, set, frozenset, OrderedDict, NamedTuple and custom objects!

    **Pycon 2016 Talk**
    I gave a talk about how DeepDiff does what it does at Pycon 2016.
    `Diff it to Dig it Pycon 2016 video <https://www.youtube.com/watch?v=J5r99eJIxF4>`_

    And here is more info: http://zepworks.com/blog/diff-it-to-digg-it/

    **Examples**

    Importing
        >>> from deepdiff import DeepDiff
        >>> from pprint import pprint
        >>> from __future__ import print_function # In case running on Python 2

    Same object returns empty
        >>> t1 = {1:1, 2:2, 3:3}
        >>> t2 = t1
        >>> print(DeepDiff(t1, t2))
        {}

    Type of an item has changed
        >>> t1 = {1:1, 2:2, 3:3}
        >>> t2 = {1:1, 2:"2", 3:3}
        >>> pprint(DeepDiff(t1, t2), indent=2)
        { 'type_changes': { 'root[2]': { 'new_type': <class 'str'>,
                                         'new_value': '2',
                                         'old_type': <class 'int'>,
                                         'old_value': 2}}}

    Value of an item has changed
        >>> t1 = {1:1, 2:2, 3:3}
        >>> t2 = {1:1, 2:4, 3:3}
        >>> pprint(DeepDiff(t1, t2, verbose_level=0), indent=2)
        {'values_changed': {'root[2]': {'new_value': 4, 'old_value': 2}}}

    Item added and/or removed
        >>> t1 = {1:1, 3:3, 4:4}
        >>> t2 = {1:1, 3:3, 5:5, 6:6}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (ddiff)
        {'dictionary_item_added': {'root[5]', 'root[6]'},
         'dictionary_item_removed': {'root[4]'}}

    Set verbose level to 2 in order to see the added or removed items with their values
        >>> t1 = {1:1, 3:3, 4:4}
        >>> t2 = {1:1, 3:3, 5:5, 6:6}
        >>> ddiff = DeepDiff(t1, t2, verbose_level=2)
        >>> pprint(ddiff, indent=2)
        { 'dictionary_item_added': {'root[5]': 5, 'root[6]': 6},
          'dictionary_item_removed': {'root[4]': 4}}

    String difference
        >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":"world"}}
        >>> t2 = {1:1, 2:4, 3:3, 4:{"a":"hello", "b":"world!"}}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (ddiff, indent = 2)
        { 'values_changed': { 'root[2]': {'new_value': 4, 'old_value': 2},
                              "root[4]['b']": { 'new_value': 'world!',
                                                'old_value': 'world'}}}


    String difference 2
        >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":"world!\nGoodbye!\n1\n2\nEnd"}}
        >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":"world\n1\n2\nEnd"}}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (ddiff, indent = 2)
        { 'values_changed': { "root[4]['b']": { 'diff': '--- \n'
                                                        '+++ \n'
                                                        '@@ -1,5 +1,4 @@\n'
                                                        '-world!\n'
                                                        '-Goodbye!\n'
                                                        '+world\n'
                                                        ' 1\n'
                                                        ' 2\n'
                                                        ' End',
                                                'new_value': 'world\n1\n2\nEnd',
                                                'old_value': 'world!\n'
                                                            'Goodbye!\n'
                                                            '1\n'
                                                            '2\n'
                                                            'End'}}}

        >>>
        >>> print (ddiff['values_changed']["root[4]['b']"]["diff"])
        ---
        +++
        @@ -1,5 +1,4 @@
        -world!
        -Goodbye!
        +world
         1
         2
         End

    Type change
        >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
        >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":"world\n\n\nEnd"}}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (ddiff, indent = 2)
        { 'type_changes': { "root[4]['b']": { 'new_type': <class 'str'>,
                                              'new_value': 'world\n\n\nEnd',
                                              'old_type': <class 'list'>,
                                              'old_value': [1, 2, 3]}}}

    And if you don't care about the value of items that have changed type, please set verbose level to 0
        >>> t1 = {1:1, 2:2, 3:3}
        >>> t2 = {1:1, 2:"2", 3:3}
        >>> pprint(DeepDiff(t1, t2, verbose_level=0), indent=2)
        { 'type_changes': { 'root[2]': { 'new_type': <class 'str'>,
                                         'old_type': <class 'int'>}}}

    List difference
        >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3, 4]}}
        >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2]}}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (ddiff, indent = 2)
        {'iterable_item_removed': {"root[4]['b'][2]": 3, "root[4]['b'][3]": 4}}

    List difference 2:
        >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
        >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 3, 2, 3]}}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (ddiff, indent = 2)
        { 'iterable_item_added': {"root[4]['b'][3]": 3},
          'values_changed': { "root[4]['b'][1]": {'new_value': 3, 'old_value': 2},
                              "root[4]['b'][2]": {'new_value': 2, 'old_value': 3}}}

    List difference ignoring order or duplicates: (with the same dictionaries as above)
        >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
        >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 3, 2, 3]}}
        >>> ddiff = DeepDiff(t1, t2, ignore_order=True)
        >>> print (ddiff)
        {}

    List difference ignoring order but reporting repetitions:
        >>> from deepdiff import DeepDiff
        >>> from pprint import pprint
        >>> t1 = [1, 3, 1, 4]
        >>> t2 = [4, 4, 1]
        >>> ddiff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True)
        >>> pprint(ddiff, indent=2)
        { 'iterable_item_removed': {'root[1]': 3},
          'repetition_change': { 'root[0]': { 'new_indexes': [2],
                                              'new_repeat': 1,
                                              'old_indexes': [0, 2],
                                              'old_repeat': 2,
                                              'value': 1},
                                 'root[3]': { 'new_indexes': [0, 1],
                                              'new_repeat': 2,
                                              'old_indexes': [3],
                                              'old_repeat': 1,
                                              'value': 4}}}

    List that contains dictionary:
        >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, {1:1, 2:2}]}}
        >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, {1:3}]}}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (ddiff, indent = 2)
        { 'dictionary_item_removed': {"root[4]['b'][2][2]"},
          'values_changed': {"root[4]['b'][2][1]": {'new_value': 3, 'old_value': 1}}}

    Sets:
        >>> t1 = {1, 2, 8}
        >>> t2 = {1, 2, 3, 5}
        >>> ddiff = DeepDiff(t1, t2)
        >>> pprint (DeepDiff(t1, t2))
        {'set_item_added': {'root[5]', 'root[3]'}, 'set_item_removed': {'root[8]'}}

    Named Tuples:
        >>> from collections import namedtuple
        >>> Point = namedtuple('Point', ['x', 'y'])
        >>> t1 = Point(x=11, y=22)
        >>> t2 = Point(x=11, y=23)
        >>> pprint (DeepDiff(t1, t2))
        {'values_changed': {'root.y': {'new_value': 23, 'old_value': 22}}}

    Custom objects:
        >>> class ClassA(object):
        ...     a = 1
        ...     def __init__(self, b):
        ...         self.b = b
        ...
        >>> t1 = ClassA(1)
        >>> t2 = ClassA(2)
        >>>
        >>> pprint(DeepDiff(t1, t2))
        {'values_changed': {'root.b': {'new_value': 2, 'old_value': 1}}}

    Object attribute added:
        >>> t2.c = "new attribute"
        >>> pprint(DeepDiff(t1, t2))
        {'attribute_added': {'root.c'},
         'values_changed': {'root.b': {'new_value': 2, 'old_value': 1}}}

    Approximate decimals comparison (Significant digits after the point):
        >>> t1 = Decimal('1.52')
        >>> t2 = Decimal('1.57')
        >>> DeepDiff(t1, t2, significant_digits=0)
        {}
        >>> DeepDiff(t1, t2, significant_digits=1)
        {'values_changed': {'root': {'old_value': Decimal('1.52'), 'new_value': Decimal('1.57')}}}

    Approximate float comparison (Significant digits after the point):
        >>> t1 = [ 1.1129, 1.3359 ]
        >>> t2 = [ 1.113, 1.3362 ]
        >>> pprint(DeepDiff(t1, t2, significant_digits=3))
        {}
        >>> pprint(DeepDiff(t1, t2))
        {'values_changed': {'root[0]': {'new_value': 1.113, 'old_value': 1.1129},
                            'root[1]': {'new_value': 1.3362, 'old_value': 1.3359}}}
        >>> pprint(DeepDiff(1.23*10**20, 1.24*10**20, significant_digits=1))
        {'values_changed': {'root': {'new_value': 1.24e+20, 'old_value': 1.23e+20}}}
    """

    show_warning = True

    def __init__(self, t1, t2,
                 ignore_order=False, report_repetition=False, significant_digits=None,
                 exclude_paths=set(), exclude_types=set(), verbose_level=1, **kwargs):
        if kwargs:
            raise ValueError(("The following parameter(s) are not valid: %s\n"
                              "The valid parameters are ignore_order, report_repetition, significant_digits,"
                              "exclude_paths, exclude_types and verbose_level.") % ', '.join(kwargs.keys()))
        self.ignore_order = ignore_order
        self.report_repetition = report_repetition
        self.exclude_paths = set(exclude_paths)
        self.exclude_types = set(exclude_types)
        self.exclude_types_tuple = tuple(exclude_types)  # we need tuple for checking isinstance
        self.verbose_level = verbose_level
        self.hashes = {}

        if significant_digits is not None and significant_digits < 0:
            raise ValueError("significant_digits must be None or a non-negative integer")
        self.significant_digits = significant_digits

        self.update({"type_changes": {}, "dictionary_item_added": self.__set_or_dict(),
                     "dictionary_item_removed": self.__set_or_dict(),
                     "values_changed": {}, "unprocessed": [], "iterable_item_added": {}, "iterable_item_removed": {},
                     "attribute_added": self.__set_or_dict(), "attribute_removed": self.__set_or_dict(),
                     "set_item_removed": set([]),
                     "set_item_added": set([]), "repetition_change": {}})

        self.__diff(t1, t2, parents_ids=frozenset({id(t1)}))

        empty_keys = [k for k, v in getattr(self, items)() if not v]

        for k in empty_keys:
            del self[k]

    def __set_or_dict(self):
        return {} if self.verbose_level >= 2 else set()

    def __extend_result_list(self, keys, parent, report_obj, print_as_attribute=False, obj=None):
        key_text = "%s{}".format(INDEX_VS_ATTRIBUTE[print_as_attribute])
        for key in keys:
            key_formatted = "'%s'" % key if not print_as_attribute and isinstance(key, strings) else key
            key_in_report = key_text % (parent, key_formatted)

            item = obj[key] if obj else key
            if not self.__skip_this(item, None, key_in_report):
                if obj and self.verbose_level >= 2:
                    report_obj[key_in_report] = obj[key]
                else:
                    report_obj.add(key_in_report)

    @staticmethod
    def __add_to_frozen_set(parents_ids, item_id):
        parents_ids = set(parents_ids)
        parents_ids.add(item_id)
        return frozenset(parents_ids)

    def __diff_obj(self, t1, t2, parent, parents_ids=frozenset({}), is_namedtuple=False):
        """Difference of 2 objects"""
        try:
            if is_namedtuple:
                t1 = t1._asdict()
                t2 = t2._asdict()
            else:
                t1 = t1.__dict__
                t2 = t2.__dict__
        except AttributeError:
            try:
                t1 = {i: getattr(t1, i) for i in t1.__slots__}
                t2 = {i: getattr(t2, i) for i in t2.__slots__}
            except AttributeError:
                self['unprocessed'].append("%s: %s and %s" % (parent, t1, t2))
                return

        self.__diff_dict(t1, t2, parent, parents_ids, print_as_attribute=True)

    def __skip_this(self, t1, t2, parent):
        skip = False
        if parent in self.exclude_paths:
            skip = True
        else:
            if isinstance(t1, self.exclude_types_tuple) or isinstance(t2, self.exclude_types_tuple):
                skip = True

        return skip

    def __diff_dict(self, t1, t2, parent, parents_ids=frozenset({}), print_as_attribute=False):
        """Difference of 2 dictionaries"""
        if print_as_attribute:
            item_added_key = "attribute_added"
            item_removed_key = "attribute_removed"
            parent_text = "%s.%s"
        else:
            item_added_key = "dictionary_item_added"
            item_removed_key = "dictionary_item_removed"
            parent_text = "%s[%s]"

        t1_keys = set(t1.keys())
        t2_keys = set(t2.keys())

        t_keys_intersect = t2_keys.intersection(t1_keys)

        t_keys_added = t2_keys - t_keys_intersect
        t_keys_removed = t1_keys - t_keys_intersect

        if t_keys_added:
            self.__extend_result_list(keys=t_keys_added, parent=parent,
                                      report_obj=self[item_added_key], print_as_attribute=print_as_attribute, obj=t2)

        if t_keys_removed:
            self.__extend_result_list(keys=t_keys_removed, parent=parent,
                                      report_obj=self[item_removed_key], print_as_attribute=print_as_attribute, obj=t1)

        self.__diff_common_children(
            t1, t2, t_keys_intersect, print_as_attribute, parents_ids, parent, parent_text)

    def __diff_common_children(self, t1, t2, t_keys_intersect, print_as_attribute, parents_ids, parent, parent_text):
        """Difference between common attributes of objects or values of common keys of dictionaries"""
        for item_key in t_keys_intersect:
            if not print_as_attribute and isinstance(item_key, strings):
                item_key_str = "'%s'" % item_key
            else:
                item_key_str = item_key

            t1_child = t1[item_key]
            t2_child = t2[item_key]

            item_id = id(t1_child)

            if parents_ids and item_id in parents_ids:
                continue

            parents_ids_added = self.__add_to_frozen_set(parents_ids, item_id)

            self.__diff(t1_child, t2_child, parent=parent_text %
                        (parent, item_key_str), parents_ids=parents_ids_added)

    def __diff_set(self, t1, t2, parent="root"):
        """Difference of sets"""
        t1_hashtable = self.__create_hashtable(t1, parent)
        t2_hashtable = self.__create_hashtable(t2, parent)

        t1_hashes = set(t1_hashtable.keys())
        t2_hashes = set(t2_hashtable.keys())

        hashes_added = t2_hashes - t1_hashes
        hashes_removed = t1_hashes - t2_hashes

        items_added = [t2_hashtable[i].item for i in hashes_added]
        items_removed = [t1_hashtable[i].item for i in hashes_removed]

        if items_removed:
            self.__extend_result_list(
                keys=items_removed, parent=parent, report_obj=self["set_item_removed"])

        if items_added:
            self.__extend_result_list(
                keys=items_added, parent=parent, report_obj=self["set_item_added"])

    def __diff_iterable(self, t1, t2, parent="root", parents_ids=frozenset({})):
        """Difference of iterables except dictionaries, sets and strings."""
        items_removed = {}
        items_added = {}

        for i, (x, y) in enumerate(zip_longest(t1, t2, fillvalue=ListItemRemovedOrAdded)):
            new_parent = "%s[%s]" % (parent, i)
            if self.__skip_this(x, y, parent=new_parent):
                continue
            if y is ListItemRemovedOrAdded:
                items_removed[new_parent] = x
            elif x is ListItemRemovedOrAdded:
                items_added[new_parent] = y
            else:
                item_id = id(x)
                if parents_ids and item_id in parents_ids:
                    continue
                parents_ids_added = self.__add_to_frozen_set(parents_ids, item_id)
                self.__diff(x, y, "%s[%s]" % (parent, i), parents_ids_added)

        self["iterable_item_removed"].update(items_removed)
        self["iterable_item_added"].update(items_added)

    def __diff_str(self, t1, t2, parent):
        """Compare strings"""
        if '\n' in t1 or '\n' in t2:
            diff = difflib.unified_diff(
                t1.splitlines(), t2.splitlines(), lineterm='')
            diff = list(diff)
            if diff:
                diff = '\n'.join(diff)
                self["values_changed"][parent] = RemapDict(
                    old_value=t1, new_value=t2, diff=diff)
        elif t1 != t2:
            self["values_changed"][parent] = RemapDict(old_value=t1, new_value=t2)

    def __diff_tuple(self, t1, t2, parent, parents_ids):
        # Checking to see if it has _fields. Which probably means it is a named
        # tuple.
        try:
            t1._asdict
        # It must be a normal tuple
        except AttributeError:
            self.__diff_iterable(t1, t2, parent, parents_ids)
        # We assume it is a namedtuple then
        else:
            self.__diff_obj(t1, t2, parent, parents_ids, is_namedtuple=True)

    def __create_hashtable(self, t, parent):
        """Create hashtable of {item_hash: item}"""

        def add_hash(hashes, item_hash, item, i):
            if item_hash in hashes:
                hashes[item_hash].indexes.append(i)
            else:
                hashes[item_hash] = IndexedHash([i], item)

        hashes = {}
        for (i, item) in enumerate(t):
            try:
                hashes_all = DeepHash(item, hashes=self.hashes)
                item_hash = hashes_all.get(id(item), item)
            except Exception as e:  # pragma: no cover
                logger.warning("Can not produce a hash for %s item in %s and "
                               "thus not counting this object: %s" % (item, parent), e)
            else:
                if item_hash is hashes_all.unprocessed:  # pragma: no cover
                    logger.warning("%s item in %s was not processed while hashing "
                                   "thus not counting this object." % (item, parent))
                else:
                    add_hash(hashes, item_hash, item, i)
        return hashes

    def __diff_iterable_with_contenthash(self, t1, t2, parent):
        """Diff of unhashable iterables. Only used when ignoring the order."""
        t1_hashtable = self.__create_hashtable(t1, parent)
        t2_hashtable = self.__create_hashtable(t2, parent)

        t1_hashes = set(t1_hashtable.keys())
        t2_hashes = set(t2_hashtable.keys())

        hashes_added = t2_hashes - t1_hashes
        hashes_removed = t1_hashes - t2_hashes

        if self.report_repetition:
            items_added = {"%s[%s]" % (parent, i): t2_hashtable[
                hash_value].item for hash_value in hashes_added for i in t2_hashtable[hash_value].indexes}

            items_removed = {"%s[%s]" % (parent, i): t1_hashtable[
                hash_value].item for hash_value in hashes_removed for i in t1_hashtable[hash_value].indexes}

            items_intersect = t2_hashes.intersection(t1_hashes)

            for key in items_intersect:
                t1_indexes = t1_hashtable[key].indexes
                t2_indexes = t2_hashtable[key].indexes
                t1_indexes_len = len(t1_indexes)
                t2_indexes_len = len(t2_indexes)
                if t1_indexes_len != t2_indexes_len:
                    t1_item_and_index = t1_hashtable[key]
                    repetition_change = {"%s[%s]" % (parent, t1_item_and_index.indexes[0]): RemapDict(
                        old_repeat=t1_indexes_len,
                        new_repeat=t2_indexes_len,
                        old_indexes=t1_indexes,
                        new_indexes=t2_indexes,
                        value=t1_item_and_index.item
                    )}
                    self['repetition_change'].update(repetition_change)

        else:
            items_added = {"%s[%s]" % (parent, t2_hashtable[hash_value].indexes[0]): t2_hashtable[
                hash_value].item for hash_value in hashes_added}

            items_removed = {"%s[%s]" % (parent, t1_hashtable[hash_value].indexes[0]): t1_hashtable[
                hash_value].item for hash_value in hashes_removed}

        self["iterable_item_removed"].update(items_removed)
        self["iterable_item_added"].update(items_added)

    def __diff_numbers(self, t1, t2, parent):
        """Diff Numbers"""

        if self.significant_digits is not None and isinstance(t1, (float, complex, Decimal)):
            # Bernhard10: I use string formatting for comparison, to be consistent with usecases where
            # data is read from files that were previousely written from python and
            # to be consistent with on-screen representation of numbers.
            # Other options would be abs(t1-t2)<10**-self.significant_digits
            # or math.is_close (python3.5+)
            # Note that abs(3.25-3.251) = 0.0009999999999998899 < 0.001
            # Note also that "{:.3f}".format(1.1135) = 1.113, but "{:.3f}".format(1.11351) = 1.114
            # For Decimals, format seems to round 2.5 to 2 and 3.5 to 4 (to closest even number)
            t1_s = ("{:.%sf}" % self.significant_digits).format(t1)
            t2_s = ("{:.%sf}" % self.significant_digits).format(t2)
            if t1_s != t2_s:
                self["values_changed"][parent] = RemapDict(
                    old_value=t1, new_value=t2)
        else:
            if t1 != t2:
                self["values_changed"][parent] = RemapDict(
                    old_value=t1, new_value=t2)

    def __diff_types(self, t1, t2, parent):
        """Diff types"""

        self["type_changes"][parent] = RemapDict(old_type=type(t1), new_type=type(t2))
        if self.verbose_level:
            self["type_changes"][parent].update(old_value=t1, new_value=t2)

    def __diff(self, t1, t2, parent="root", parents_ids=frozenset({})):
        """The main diff method"""

        if t1 is t2:
            return

        if self.__skip_this(t1, t2, parent):
            return

        if type(t1) != type(t2):
            self.__diff_types(t1, t2, parent)

        elif isinstance(t1, strings):
            self.__diff_str(t1, t2, parent)

        elif isinstance(t1, numbers):
            self.__diff_numbers(t1, t2, parent)

        elif isinstance(t1, MutableMapping):
            self.__diff_dict(t1, t2, parent, parents_ids)

        elif isinstance(t1, tuple):
            self.__diff_tuple(t1, t2, parent, parents_ids)

        elif isinstance(t1, (set, frozenset)):
            self.__diff_set(t1, t2, parent=parent)

        elif isinstance(t1, Iterable):
            if self.ignore_order:
                self.__diff_iterable_with_contenthash(t1, t2, parent)
            else:
                self.__diff_iterable(t1, t2, parent, parents_ids)

        else:
            self.__diff_obj(t1, t2, parent, parents_ids)

        return


if __name__ == "__main__":  # pragma: no cover
    if not py3:
        sys.exit("Please run with Python 3 to verify the doc strings.")
    import doctest
    doctest.testmod()
