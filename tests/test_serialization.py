#!/usr/bin/env python
# -*- coding: utf-8 -*-
from deepdiff import DeepDiff

import logging
logging.disable(logging.CRITICAL)


class TestDeepAdditions:
    """Tests for Additions and Subtractions."""

    def test_serialization_text(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3]}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world\n\n\nEnd"}}
        ddiff = DeepDiff(t1, t2)
        assert "builtins.list" in ddiff.to_json_pickle()

    def test_deserialization(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3]}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world\n\n\nEnd"}}
        ddiff = DeepDiff(t1, t2)
        jsoned = ddiff.to_json_pickle()
        ddiff2 = DeepDiff.from_json(jsoned)
        assert ddiff == ddiff2

    def test_serialization_tree(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3]}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world\n\n\nEnd"}}
        ddiff = DeepDiff(t1, t2, view='tree')
        pickle_jsoned = ddiff.to_json_pickle()
        assert "world" in pickle_jsoned
        jsoned = ddiff.to_json()
        assert "world" in jsoned

    def test_deserialization_tree(self):
        t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3]}}
        t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world\n\n\nEnd"}}
        ddiff = DeepDiff(t1, t2, view='tree')
        jsoned = ddiff.to_json_pickle()
        ddiff2 = DeepDiff.from_json(jsoned)
        assert 'type_changes' in ddiff2

    def test_deleting_serialization_cache_when_using_the_property(self):
        t1 = {1: 1}
        t2 = {1: 2}
        ddiff = DeepDiff(t1, t2)
        assert hasattr(ddiff, '_json') is False
        ddiff.json
        assert hasattr(ddiff, '_json')
        del ddiff.json
        assert hasattr(ddiff, '_json') is False
