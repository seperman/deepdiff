#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import difflib
import logging

from decimal import Decimal

from collections import MutableMapping
from collections import Iterable

from deepdiff.helper import py3, strings, numbers, ListItemRemovedOrAdded, IndexedHash
from deepdiff.model import RemapDict, ResultDict, TextStyleResultDict, RefStyleResultDict, DiffLevel
from deepdiff.model import DictRelationship, AttributeRelationship
from deepdiff.model import SubscriptableIterableRelationship, NonSubscriptableIterableRelationship, SetRelationship
from deepdiff.contenthash import DeepHash

if py3:  # pragma: no cover
    from itertools import zip_longest
else:  # pragma: no cover
    from itertools import izip_longest as zip_longest

logger = logging.getLogger(__name__)

class DeepDiff(ResultDict):

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
                 exclude_paths=set(), exclude_types=set(), verbose_level=1, default_view='text',
                 **kwargs):
        if kwargs:
            raise ValueError(("The following parameter(s) are not valid: %s\n"
                              "The valid parameters are ignore_order, report_repetition, significant_digits,"
                              "exclude_paths, exclude_types, verbose_level and default_view.") % ', '.join(kwargs.keys()))

        self.ignore_order = ignore_order
        self.report_repetition = report_repetition
        self.exclude_paths = set(exclude_paths)
        self.exclude_types = set(exclude_types)
        self.exclude_types_tuple = tuple(exclude_types)  # we need tuple for checking isinstance
        self.hashes = {}

        if significant_digits is not None and significant_digits < 0:
            raise ValueError("significant_digits must be None or a non-negative integer")
        self.significant_digits = significant_digits

        self.result_refs = RefStyleResultDict()

        root = DiffLevel(t1, t2)
        self.__diff(root, parents_ids=frozenset({id(t1)}))

        self.result_refs.cleanup()

        self.result_text = TextStyleResultDict(verbose_level, self.result_refs)
        self.result_text.cleanup()   # clean up text-style result dictionary

        if default_view == 'ref':          # Allow one of our views to be accessible directly via this object
            self.update(self.result_refs)
        else:
            self.update(self.result_text)  # be compatible to DeepDiff 2.x if user didn't specify otherwise

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
            self.result_refs[report_type].add(level)

    @staticmethod
    def __add_to_frozen_set(parents_ids, item_id):
        parents_ids = set(parents_ids)
        parents_ids.add(item_id)
        return frozenset(parents_ids)

    def __diff_obj(self, level, parents_ids=frozenset({}), is_namedtuple=False):
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
                t1 = {i: getattr(level.t1, i) for i in level.t1.__slots__}
                t2 = {i: getattr(level.t2, i) for i in level.t2.__slots__}
            except AttributeError:
                self.__report_result('unprocessed', level)
                return

        self.__diff_dict(level, parents_ids, print_as_attribute=True, override=True, override_t1=t1, override_t2=t2)

    def __skip_this(self, level):
        """
        Check whether this comparison should be skipped because one of the objects to compare meets exclusion criteria.
        :rtype: bool
        """
        skip = False
        if level.path() in self.exclude_paths:
            skip = True
        else:
            if isinstance(level.t1, self.exclude_types_tuple) or isinstance(level.t2, self.exclude_types_tuple):
                skip = True

        return skip

    def __diff_dict(self, level, parents_ids=frozenset({}), print_as_attribute=False,
                    override=False, override_t1=None, override_t2=None):
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

        t_keys_intersect = t2_keys.intersection(t1_keys)

        t_keys_added = t2_keys - t_keys_intersect
        t_keys_removed = t1_keys - t_keys_intersect

        for key in t_keys_added:
            change_level = level.branch_deeper(None, t2[key],
                                               child_relationship_class=rel_class, child_relationship_param=key)
            self.__report_result(item_added_key, change_level)

        for key in t_keys_removed:
            change_level = level.branch_deeper(t1[key], None,
                                               child_relationship_class=rel_class, child_relationship_param=key)
            self.__report_result(item_removed_key, change_level)

        for key in t_keys_intersect:  # key present in both dicts - need to compare values
            item_id = id(t1[key])
            if parents_ids and item_id in parents_ids:
                continue
            parents_ids_added = self.__add_to_frozen_set(parents_ids, item_id)

            # Go one level deeper
            next_level = level.branch_deeper(t1[key], t2[key],
                                             child_relationship_class=rel_class, child_relationship_param=key)
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
            change_level = level.branch_deeper(None, item,
                                               child_relationship_class=SetRelationship)
            self.__report_result('set_item_added', change_level)

        for item in items_removed:
            change_level = level.branch_deeper(item, None,
                                               child_relationship_class=SetRelationship)
            self.__report_result('set_item_removed', change_level)

    def __diff_iterable(self, level, parents_ids=frozenset({})):
        """Difference of iterables except dictionaries, sets and strings."""
        try:
            if getattr(level.t1, '__getitem__') and getattr(level.t2, '__getitem__'):
                return self.__diff_iterable_subscriptable(level, parents_ids)
        except AttributeError:
            # Temporarily fix handling of non-subscriptable iterables by pretending they are subscriptable.
            # See test for further comments.
            # TODO: This fakes input data! Must fix this!
            level.t1 = list(level.t1)
            level.t2 = list(level.t2)
            return self.__diff_iterable_subscriptable(level, parents_ids)

    def __diff_iterable_subscriptable(self, level, parents_ids=frozenset({})):
        """Difference of subscriptable iterables, like lists"""
        for i, (x, y) in enumerate(zip_longest(level.t1, level.t2, fillvalue=ListItemRemovedOrAdded)):
            if y is ListItemRemovedOrAdded:    # item removed completely
                change_level = level.branch_deeper(level.t1[i], None,
                                                   child_relationship_class=SubscriptableIterableRelationship,
                                                   child_relationship_param=i)
                self.__report_result('iterable_item_removed', change_level)

            elif x is ListItemRemovedOrAdded:  # new item added
                change_level = level.branch_deeper(None, level.t2[i],
                                                   child_relationship_class=SubscriptableIterableRelationship,
                                                   child_relationship_param=i)
                self.__report_result('iterable_item_added', change_level)

            else:                              # check if item value has changed
                item_id = id(x)
                if parents_ids and item_id in parents_ids:
                    continue
                parents_ids_added = self.__add_to_frozen_set(parents_ids, item_id)

                # Go one level deeper
                next_level = level.branch_deeper(x, y,
                                                 child_relationship_class=SubscriptableIterableRelationship,
                                                 child_relationship_param=i)
                self.__diff(next_level, parents_ids_added)

    def __diff_str(self, level):
        """Compare strings"""
        if level.t1 == level.t2:
            return

        # do we add a diff for convenience?
        if '\n' in level.t1 or '\n' in level.t2:
            diff = difflib.unified_diff(
                level.t1.splitlines(), level.t2.splitlines(), lineterm='')
            diff = list(diff)
            if diff:
                level.additional['diff'] = '\n'.join(diff)

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

    def __create_hashtable(self, t, level):
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
                logger.warning("Can not produce a hash for %s and "
                               "thus not counting this object: %s" % level.path(), e)
            else:
                if item_hash is hashes_all.unprocessed:  # pragma: no cover
                    logger.warning("Item %s was not processed while hashing "
                                   "thus not counting this object." % level.path())
                else:
                    add_hash(hashes, item_hash, item, i)
        return hashes

    def __diff_iterable_with_contenthash(self, level):
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
                    change_level = level.branch_deeper(None, t2_hashtable[hash_value].item,
                                                       child_relationship_class=SubscriptableIterableRelationship,    # TODO: that might be a lie!
                                                       child_relationship_param=i)                                    # TODO: what is this value exactly?
                    self.__report_result('iterable_item_added', change_level)

            for hash_value in hashes_removed:
                for i in t1_hashtable[hash_value].indexes:
                    change_level = level.branch_deeper(t1_hashtable[hash_value].item, None,
                                                       child_relationship_class=SubscriptableIterableRelationship,    # TODO: that might be a lie!
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
                        t1_hashtable[hash_value].item, t2_hashtable[hash_value].item,  # nb: those are equal!
                        child_relationship_class=SubscriptableIterableRelationship,    # TODO: that might be a lie!
                        child_relationship_param=t1_hashtable[hash_value].indexes[0])
                    repetition_change_level.additional['rep'] = RemapDict(
                        old_repeat=t1_indexes_len,
                        new_repeat=t2_indexes_len,
                        old_indexes=t1_indexes,
                        new_indexes=t2_indexes)
                    self.__report_result('repetition_change', repetition_change_level)

        else:
            for hash_value in hashes_added:
                change_level = level.branch_deeper(None, t2_hashtable[hash_value].item,
                                                   child_relationship_class=SubscriptableIterableRelationship,    # TODO: that might be a lie!
                                                   child_relationship_param=t2_hashtable[hash_value].indexes[0])  # TODO: what is this value exactly?
                self.__report_result('iterable_item_added', change_level)

            for hash_value in hashes_removed:
                change_level = level.branch_deeper(t1_hashtable[hash_value].item, None,
                                                   child_relationship_class=SubscriptableIterableRelationship,    # TODO: that might be a lie!
                                                   child_relationship_param=t1_hashtable[hash_value].indexes[0])
                self.__report_result('iterable_item_removed', change_level)

    def __diff_numbers(self, level):
        """Diff Numbers"""

        if self.significant_digits is not None and isinstance(level.t1, (float, complex, Decimal)):
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
            if t1_s != t2_s:
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

        if type(level.t1) != type(level.t2):
            self.__diff_types(level)

        elif isinstance(level.t1, strings):
            self.__diff_str(level)

        elif isinstance(level.t1, numbers):
            self.__diff_numbers(level)

        elif isinstance(level.t1, MutableMapping):
            self.__diff_dict(level, parents_ids)

        elif isinstance(level.t1, tuple):
            self.__diff_tuple(level, parents_ids)

        elif isinstance(level.t1, (set, frozenset)):
            self.__diff_set(level)

        elif isinstance(level.t1, Iterable):
            if self.ignore_order:
                self.__diff_iterable_with_contenthash(level)
            else:
                self.__diff_iterable(level, parents_ids)

        else:
            self.__diff_obj(level, parents_ids)

        return


if __name__ == "__main__":  # pragma: no cover
    if not py3:
        sys.exit("Please run with Python 3 to verify the doc strings.")
    import doctest
    doctest.testmod()
