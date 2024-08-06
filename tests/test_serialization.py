#!/usr/bin/env python
import os
import json
import sys
import pytest
import datetime
import numpy as np
from typing import NamedTuple, Optional
from pickle import UnpicklingError
from decimal import Decimal
from collections import Counter
from deepdiff import DeepDiff
from deepdiff.helper import pypy3, py_current_version, np_ndarray, Opcode, SetOrdered
from deepdiff.serialization import (
    pickle_load, pickle_dump, ForbiddenModule, ModuleNotFoundError,
    MODULE_NOT_FOUND_MSG, FORBIDDEN_MODULE_MSG, pretty_print_diff,
    load_path_content, UnsupportedFormatErr, json_dumps, json_loads)
from conftest import FIXTURES_DIR
from tests import PicklableClass

import logging
logging.disable(logging.CRITICAL)

t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3]}}
t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world\n\n\nEnd"}}


class SomeStats(NamedTuple):
    counter: Optional[Counter]
    context_aware_counter: Optional[Counter] = None
    min_int: Optional[int] = 0
    max_int: Optional[int] = 0


field_stats1 = SomeStats(
    counter=Counter(["a", "a", "b"]),
    max_int=10
)


class TestSerialization:
    """Tests for Serializations."""

    def test_serialization_text(self):
        ddiff = DeepDiff(t1, t2)
        assert "builtins.list" in ddiff.to_json_pickle()
        jsoned = ddiff.to_json()
        assert "world" in jsoned

    def test_deserialization(self):
        ddiff = DeepDiff(t1, t2)
        jsoned = ddiff.to_json_pickle()
        ddiff2 = DeepDiff.from_json_pickle(jsoned)
        assert ddiff == ddiff2

    def test_serialization_tree(self):
        ddiff = DeepDiff(t1, t2, view='tree')
        pickle_jsoned = ddiff.to_json_pickle()
        assert "world" in pickle_jsoned
        jsoned = ddiff.to_json()
        assert "world" in jsoned

    def test_deserialization_tree(self):
        ddiff = DeepDiff(t1, t2, view='tree')
        jsoned = ddiff.to_json_pickle()
        ddiff2 = DeepDiff.from_json_pickle(jsoned)
        assert 'type_changes' in ddiff2

    def test_serialize_custom_objects_throws_error(self):
        class A:
            pass

        class B:
            pass

        t1 = A()
        t2 = B()
        ddiff = DeepDiff(t1, t2)
        with pytest.raises(TypeError):
            ddiff.to_json()

    def test_serialize_custom_objects_with_default_mapping(self):
        class A:
            pass

        class B:
            pass

        t1 = A()
        t2 = B()
        ddiff = DeepDiff(t1, t2)
        default_mapping = {A: lambda x: 'obj A', B: lambda x: 'obj B'}
        result = ddiff.to_json(default_mapping=default_mapping)
        expected_result = {"type_changes": {"root": {"old_type": "A", "new_type": "B", "old_value": "obj A", "new_value": "obj B"}}}
        assert expected_result == json.loads(result)

    # These lines are long but make it easier to notice the difference:
    @pytest.mark.parametrize('verbose_level, expected', [
        (0, {"type_changes": {"root[0]": {"old_type": str, "new_type": int}}, "dictionary_item_added": ["root[1][5]"], "dictionary_item_removed": ["root[1][3]"], "iterable_item_added": {"root[2]": "d"}}),
        (1, {"type_changes": {"root[0]": {"old_type": str, "new_type": int, "old_value": "a", "new_value": 10}}, "dictionary_item_added": ["root[1][5]"], "dictionary_item_removed": ["root[1][3]"], "values_changed": {"root[1][1]": {"new_value": 2, "old_value": 1}}, "iterable_item_added": {"root[2]": "d"}}),
        (2, {"type_changes": {"root[0]": {"old_type": str, "new_type": int, "old_value": "a", "new_value": 10}}, "dictionary_item_added": {"root[1][5]": 6}, "dictionary_item_removed": {"root[1][3]": 4}, "values_changed": {"root[1][1]": {"new_value": 2, "old_value": 1}}, "iterable_item_added": {"root[2]": "d"}}),
    ])
    def test_to_dict_at_different_verbose_level(self, verbose_level, expected):
        t1 = ['a', {1: 1, 3: 4}, ]
        t2 = [10, {1: 2, 5: 6}, 'd']

        ddiff = DeepDiff(t1, t2, verbose_level=verbose_level)
        assert expected == ddiff.to_dict()


@pytest.mark.skipif(pypy3, reason='clevercsv is not supported in pypy3')
class TestLoadContet:

    @pytest.mark.parametrize('path1, validate', [
        ('t1.json', lambda x: x[0]['key1'] == 'value1'),
        ('t1.yaml', lambda x: x[0][0] == 'name'),
        ('t1.toml', lambda x: x['servers']['alpha']['ip'] == '10.0.0.1'),
        ('t1.csv', lambda x: x[0]['last_name'] == 'Nobody'),
        ('t1.pickle', lambda x: x[1] == 1),
    ])
    def test_load_path_content(self, path1, validate):
        path = os.path.join(FIXTURES_DIR, path1)
        result = load_path_content(path)
        assert validate(result)

    def test_load_path_content_when_unsupported_format(self):
        path = os.path.join(FIXTURES_DIR, 't1.unsupported')
        with pytest.raises(UnsupportedFormatErr):
            load_path_content(path)


class TestPickling:

    def test_serialize(self):
        obj = [1, 2, 3, None, {10: 11E2}, frozenset(['a', 'c']), SetOrdered([2, 1]),
               datetime.datetime(2022, 4, 10, 0, 40, 41, 357857), datetime.time(11), Decimal('11.2'), 123.11]
        serialized = pickle_dump(obj)
        loaded = pickle_load(serialized)
        assert obj == loaded

    @pytest.mark.skipif(pypy3, reason='short pickle not supported in pypy3')
    def test_pickle_that_is_string(self):
        serialized_str = 'DeepDiff Delta Payload v0-0-1\nBlah'
        with pytest.raises(UnpicklingError):
            pickle_load(serialized_str)

    def test_custom_object_deserialization_fails_without_explicit_permission(self):
        obj = PicklableClass(10)
        module_dot_name = 'tests.{}'.format(PicklableClass.__name__)

        serialized = pickle_dump(obj)

        expected_msg = FORBIDDEN_MODULE_MSG.format(module_dot_name)
        with pytest.raises(ForbiddenModule) as excinfo:
            pickle_load(serialized)
        assert expected_msg == str(excinfo.value)

        # Explicitly allowing the module to be loaded
        loaded = pickle_load(serialized, safe_to_import={module_dot_name})
        assert obj == loaded

        # Explicitly allowing the module to be loaded. It can take a list instead of a set.
        loaded2 = pickle_load(serialized, safe_to_import=[module_dot_name])
        assert obj == loaded2

    def test_unpickling_object_that_is_not_imported_raises_error(self):

        def get_the_pickle():
            import wave
            obj = wave.Error
            return pickle_dump(obj)

        serialized = get_the_pickle()
        # Making sure that the module is unloaded.
        del sys.modules['wave']
        module_dot_name = 'wave.Error'

        expected_msg = MODULE_NOT_FOUND_MSG.format(module_dot_name)
        with pytest.raises(ModuleNotFoundError) as excinfo:
            pickle_load(serialized, safe_to_import=module_dot_name)
        assert expected_msg == str(excinfo.value)


class TestDeepDiffPretty:
    """Tests for pretty() method of DeepDiff"""

    class TestingClass:
        one = 1

    testing_class = TestingClass

    @pytest.mark.parametrize('t1, t2, item_path, old_type, new_type, old_val_displayed, new_val_displayed',
                             [
                                 [{2: 2, 4: 4}, {2: 'b', 4: 4}, 'root[2]', 'int', 'str', '2', '"b"'],
                                 [[1, 2, 3], [1, '2', 3], 'root[1]', 'int', 'str', '2', '"2"'],
                                 [[1, 2, 3], {1, 2, 3}, 'root', 'list', 'set', '[1, 2, 3]', '{1, 2, 3}']
                             ])
    def test_pretty_print_diff_type_changes(self, t1, t2, item_path, old_type, new_type, old_val_displayed,
                                            new_val_displayed):
        ddiff = DeepDiff(t1, t2, view='tree')
        result = pretty_print_diff(ddiff.tree['type_changes'][0])
        assert result == 'Type of {} changed from {} to {} and value changed from {} to {}.'.format(item_path, old_type, new_type, old_val_displayed, new_val_displayed)

    @pytest.mark.parametrize('t1, t2, item_path, verbose_level',
                             [
                                 [{2: 2, 4: 4}, {2: 2, 4: 4, 5: 5}, 'root[5]', 1],
                                 [{2: 2, 4: 4}, {2: 2, 4: 4, 5: 5}, 'root[5] (5)', 2],
                                 [{"foo": "bar", "foo1": "bar1"}, {"foo": "bar", "foo1": "bar1", "foo2": "bar2"},
                                  'root[\'foo2\']', 0],
                                 [{"foo": "bar", "foo1": "bar1"}, {"foo": "bar", "foo1": "bar1", "foo2": "bar2"},
                                  'root[\'foo2\'] ("bar2")', 2]
                             ])
    def test_pretty_print_diff_dictionary_item_added(self, t1, t2, item_path, verbose_level):
        ddiff = DeepDiff(t1, t2, view='tree', verbose_level=verbose_level)
        result = pretty_print_diff(ddiff.tree['dictionary_item_added'][0])
        assert result == 'Item {} added to dictionary.'.format(item_path)

    @pytest.mark.parametrize('t1, t2, item_path, verbose_level',
                             [
                                 [{2: 2, 4: 4}, {2: 2}, 'root[4]', 0],
                                 [{2: 2, 4: 4}, {2: 2}, 'root[4] (4)', 2],
                                 [{"foo": "bar", "foo1": "bar1"}, {"foo": "bar"},
                                  'root[\'foo1\']', 1],
                                 [{"foo": "bar", "foo1": "bar1"}, {"foo": "bar"},
                                  'root[\'foo1\'] ("bar1")', 2],
                             ])
    def test_pretty_print_diff_dictionary_item_removed(self, t1, t2, item_path, verbose_level):
        ddiff = DeepDiff(t1, t2, view='tree', verbose_level=verbose_level)
        result = pretty_print_diff(ddiff.tree['dictionary_item_removed'][0])
        assert result == 'Item {} removed from dictionary.'.format(item_path)

    @pytest.mark.parametrize('t1, t2, item_path, old_val_displayed, new_val_displayed',
                             [
                                 [{2: 2, 4: 4}, {2: 3, 4: 4}, 'root[2]', '2', '3'],
                                 [['a', 'b', 'c'], ['a', 'b', 'd'], 'root[2]', '"c"', '"d"']
                             ])
    def test_pretty_print_diff_values_changed(self, t1, t2, item_path, old_val_displayed, new_val_displayed):
        ddiff = DeepDiff(t1, t2, view='tree')
        result = pretty_print_diff(ddiff.tree['values_changed'][0])
        assert result == 'Value of {} changed from {} to {}.'.format(item_path, old_val_displayed, new_val_displayed)

    @pytest.mark.parametrize('t1, t2, item_path, verbose_level',
                             [
                                 [[1, 2, 3], [1, 2, 3, 4], 'root[3]', 1],
                                 [[1, 2, 3], [1, 2, 3, 4], 'root[3] (4)', 2],
                                 [["foo", "bar"], ["foo", "bar", "barbar"], 'root[2]', 0],
                                 [["foo", "bar"], ["foo", "bar", "barbar"], 'root[2] ("barbar")', 2]
                             ])
    def test_pretty_print_diff_iterable_item_added(self, t1, t2, item_path, verbose_level):
        ddiff = DeepDiff(t1, t2, view='tree', verbose_level=verbose_level)
        result = pretty_print_diff(ddiff.tree['iterable_item_added'][0])
        assert result == 'Item {} added to iterable.'.format(item_path)

    @pytest.mark.parametrize('t1, t2, item_path, verbose_level',
                             [
                                 [[1, 2, 3], [1, 2], 'root[2]', 0],
                                 [[1, 2, 3], [1, 2], 'root[2] (3)', 2],
                                 [["foo", "bar", "barbar"], ["foo", "bar"], 'root[2]', 1],
                                 [["foo", "bar", "barbar"], ["foo", "bar"], 'root[2] ("barbar")', 2]
                             ])
    def test_pretty_print_diff_iterable_item_removed(self, t1, t2, item_path, verbose_level):
        ddiff = DeepDiff(t1, t2, view='tree', verbose_level=verbose_level)
        result = pretty_print_diff(ddiff.tree['iterable_item_removed'][0])
        assert result == 'Item {} removed from iterable.'.format(item_path)

    @pytest.mark.parametrize("verbose_level", range(3))
    def test_pretty_print_diff_attribute_added(self, verbose_level):
        t1 = self.testing_class()
        t2 = self.testing_class()
        t2.two = 2

        ddiff = DeepDiff(t1, t2, view='tree', verbose_level=verbose_level)
        result = pretty_print_diff(ddiff.tree['attribute_added'][0])
        assert result == 'Attribute root.two (2) added.' if verbose_level == 2 else 'Attribute root.two added.'

    @pytest.mark.parametrize("verbose_level", range(3))
    def test_pretty_print_diff_attribute_removed(self, verbose_level):
        t1 = self.testing_class()
        t1.two = 2
        t2 = self.testing_class()

        ddiff = DeepDiff(t1, t2, view='tree', verbose_level=verbose_level)
        result = pretty_print_diff(ddiff.tree['attribute_removed'][0])

        assert result == 'Attribute root.two (2) removed.' if verbose_level == 2 else 'Attribute root.two removed.'

    @pytest.mark.parametrize('t1, t2, item_path',
                             [
                                 [{1, 2}, {1, 2, 3}, 'root[3]'],
                             ])
    def test_pretty_print_diff_set_item_added(self, t1, t2, item_path):
        ddiff = DeepDiff(t1, t2, view='tree')
        result = pretty_print_diff(ddiff.tree['set_item_added'][0])
        assert result == 'Item {} added to set.'.format(item_path)

    @pytest.mark.parametrize('t1, t2, item_path',
                             [
                                 [{1, 2, 3}, {1, 2}, 'root[3]'],
                             ])
    def test_pretty_print_diff_set_item_removed(self, t1, t2, item_path):
        ddiff = DeepDiff(t1, t2, view='tree')
        result = pretty_print_diff(ddiff.tree['set_item_removed'][0])
        assert result == 'Item {} removed from set.'.format(item_path)

    @pytest.mark.parametrize('t1, t2, item_path',
                             [
                                 [[1, 2, 3, 2], [1, 2, 3], 'root[1]'],
                             ])
    def test_pretty_print_diff_repetition_change(self, t1, t2, item_path):
        ddiff = DeepDiff(t1, t2, view='tree', ignore_order=True, report_repetition=True)
        result = pretty_print_diff(ddiff.tree['repetition_change'][0])
        assert result == 'Repetition change for item {}.'.format(item_path)

    @pytest.mark.parametrize("expected, verbose_level",
                             (
                                 ('Item root[5] added to dictionary.'
                                  '\nItem root[3] removed from dictionary.'
                                  '\nType of root[2] changed from int to str and value changed from 2 to "b".'
                                  '\nValue of root[4] changed from 4 to 5.', 0),
                                 ('Item root[5] (5) added to dictionary.'
                                  '\nItem root[3] (3) removed from dictionary.'
                                  '\nType of root[2] changed from int to str and value changed from 2 to "b".'
                                  '\nValue of root[4] changed from 4 to 5.', 2),
                             ), ids=("verbose=0", "verbose=2")
                             )
    def test_pretty_form_method(self, expected, verbose_level):
        t1 = {2: 2, 3: 3, 4: 4}
        t2 = {2: 'b', 4: 5, 5: 5}
        ddiff = DeepDiff(t1, t2, view='tree', verbose_level=verbose_level)
        result = ddiff.pretty()
        assert result == expected

    @pytest.mark.parametrize('test_num, value, func_to_convert_back', [
        (1, {'10': None}, None),
        (2, {"type_changes": {"root": {"old_type": None, "new_type": list, "new_value": ["你好", 2, 3, 5]}}}, None),
        (3, {'10': Decimal(2017)}, None),
        (4, Decimal(2017.1), None),
        (5, {1, 2, 10}, set),
        (6, datetime.datetime(2023, 10, 11), datetime.datetime.fromisoformat),
        (7, datetime.datetime.utcnow(), datetime.datetime.fromisoformat),
        (8, field_stats1, lambda x: SomeStats(**x)),
        (9, np.array([[ 101, 3533, 1998, 4532, 2024, 3415, 1012,  102]]), np.array)
    ])
    def test_json_dumps_and_loads(self, test_num, value, func_to_convert_back):
        if test_num == 8 and py_current_version < 3.8:
            print(f"Skipping test_json_dumps_and_loads #{test_num} on Python {py_current_version}")
            return
        serialized = json_dumps(value)
        back = json_loads(serialized)
        if func_to_convert_back:
            back = func_to_convert_back(back)
        if isinstance(back, np_ndarray):
            assert np.array_equal(value, back), f"test_json_dumps_and_loads test #{test_num} failed"
        else:
            assert value == back, f"test_json_dumps_and_loads test #{test_num} failed"

    def test_namedtuple_seriazliation(self):
        op_code = Opcode(tag="replace", t1_from_index=0, t1_to_index=1, t2_from_index=10, t2_to_index=20)
        serialized = json_dumps(op_code)
        expected = '{"tag":"replace","t1_from_index":0,"t1_to_index":1,"t2_from_index":10,"t2_to_index":20,"old_values":null,"new_values":null}'
        assert serialized == expected

    def test_reversed_list(self):
        items = reversed([1, 2, 3])

        serialized = json_dumps(items)
        serialized2 = json_dumps(items)

        assert '[3,2,1]' == serialized
        assert '[3,2,1]' == serialized2, "We should have copied the original list. If this returns empty, it means we exhausted the original list."

