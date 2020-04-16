#!/usr/bin/env python
import json
import sys
import pytest
import datetime
from decimal import Decimal
from deepdiff import DeepDiff
from deepdiff.serialization import (
    pickle_load, pickle_dump, ForbiddenModule, ModuleNotFoundError,
    MODULE_NOT_FOUND_MSG, FORBIDDEN_MODULE_MSG)
from ordered_set import OrderedSet
from tests import PicklableClass

import logging
logging.disable(logging.CRITICAL)

t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3]}}
t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world\n\n\nEnd"}}


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

    @pytest.mark.parametrize('verbose_level, expected', [
        (0, ''),
        (1, ''),
        (2, ''),
    ])
    def test_to_dict_is_always_at_verbose_level2(self, verbose_level, expected):
        t1 = ['a', {1: 1, 3: 4}]
        t2 = ['c', {1: 2, 5: 6}, 'd']

        ddiff = DeepDiff(t1, t2, verbose_level=verbose_level)

        # result = json.loads(ddiff.to_json())
        assert expected == ddiff.to_dict()


class TestPickling:

    def test_serialize(self):
        obj = [1, 2, 3, None, {10: 11E2}, frozenset(['a', 'c']), OrderedSet([2, 1]),
               datetime.datetime.utcnow(), datetime.time(11), Decimal('11.2'), 123.11]
        serialized = pickle_dump(obj)
        loaded = pickle_load(serialized)
        assert obj == loaded

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

    def test_unpickling_object_that_is_not_imported(self):

        def get_the_pickle():
            import wave
            obj = wave.Error
            return pickle_dump(obj)

        serialized = get_the_pickle()
        del sys.modules['wave']
        module_dot_name = 'wave.Error'

        expected_msg = MODULE_NOT_FOUND_MSG.format(module_dot_name)
        with pytest.raises(ModuleNotFoundError) as excinfo:
            pickle_load(serialized, safe_to_import=module_dot_name)
        assert expected_msg == str(excinfo.value)
