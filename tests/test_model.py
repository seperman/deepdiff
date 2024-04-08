#!/usr/bin/env python
import datetime
import logging
import pytest
from tests import CustomClass, CustomClassMisleadingRepr
from deepdiff import DeepDiff
from deepdiff.model import (DiffLevel, ChildRelationship, DictRelationship,
                            SubscriptableIterableRelationship,
                            AttributeRelationship)

logging.disable(logging.CRITICAL)


class WorkingChildRelationship(ChildRelationship):
    pass


class TestDictRelationship:
    def setup_class(cls):
        cls.customkey = CustomClass(a=13, b=37)
        cls.customkey_misleading = CustomClassMisleadingRepr(a=11, b=20)
        cls.d = {
            42: 'answer',
            'vegan': 'for life',
            cls.customkey: 1337,
            cls.customkey_misleading: 'banana'
        }

    def test_numkey(self):
        rel = DictRelationship(parent=self.d, child=self.d[42], param=42)
        assert rel.get_param_repr() == "[42]"

    def test_strkey(self):
        rel = ChildRelationship.create(
            klass=DictRelationship,
            parent=self.d,
            child=self.d['vegan'],
            param='vegan')
        result = rel.get_param_repr()
        assert result == "['vegan']"

    def test_objkey(self):
        rel = DictRelationship(
            parent=self.d, child=self.d[self.customkey], param=self.customkey)
        assert rel.get_param_repr() is None

    def test_objkey_misleading_repr(self):
        rel = DictRelationship(
            parent=self.d,
            child=self.d[self.customkey_misleading],
            param=self.customkey_misleading)
        assert rel.get_param_repr() is None


class TestListRelationship:
    def setup_class(cls):
        cls.custom = CustomClass(13, 37)
        cls.l = [1337, 'vegan', cls.custom]

    def test_min(self):
        rel = SubscriptableIterableRelationship(self.l, self.l[0], 0)
        result = rel.get_param_repr()
        assert result == "[0]"

    def test_max(self):
        rel = ChildRelationship.create(SubscriptableIterableRelationship,
                                       self.l, self.custom, 2)
        assert rel.get_param_repr() == "[2]"


class TestAttributeRelationship:
    def setup_class(cls):
        cls.custom = CustomClass(13, 37)

    def test_a(self):
        rel = AttributeRelationship(self.custom, 13, "a")
        result = rel.get_param_repr()
        assert result == ".a"


class TestDiffLevel:
    def setup_class(cls):
        # Test data
        cls.custom1 = CustomClass(a='very long text here', b=37)
        cls.custom2 = CustomClass(a=313, b=37)
        cls.t1 = {42: 'answer', 'vegan': 'for life', 1337: cls.custom1}
        cls.t2 = {
            42: 'answer',
            'vegan': 'for the animals',
            1337: cls.custom2
        }

        # Manually build diff, bottom up
        cls.lowest = DiffLevel(
            cls.custom1.a, cls.custom2.a, report_type='values_changed')

        # Test manual child relationship
        rel_int_low_t1 = AttributeRelationship(
            parent=cls.custom1, child=cls.custom1.a, param="a")
        rel_int_low_t2 = AttributeRelationship(
            parent=cls.custom2, child=cls.custom2.a, param="a")
        cls.intermediate = DiffLevel(
            cls.custom1,
            cls.custom2,
            down=cls.lowest,
            child_rel1=rel_int_low_t1,
            child_rel2=rel_int_low_t2)
        cls.lowest.up = cls.intermediate

        # Test automatic child relationship
        t1_child_rel = ChildRelationship.create(
            klass=DictRelationship,
            parent=cls.t1,
            child=cls.intermediate.t1,
            param=1337)
        t2_child_rel = ChildRelationship.create(
            klass=DictRelationship,
            parent=cls.t2,
            child=cls.intermediate.t2,
            param=1337)
        cls.highest = DiffLevel(
            cls.t1,
            cls.t2,
            down=cls.intermediate,
            child_rel1=t1_child_rel,
            child_rel2=t2_child_rel)
        cls.intermediate.up = cls.highest

    def test_all_up(self):
        assert self.lowest.all_up == self.highest

    def test_all_down(self):
        assert self.highest.all_down == self.lowest

    def test_automatic_child_rel(self):
        assert isinstance(self.highest.t1_child_rel, DictRelationship)
        assert isinstance(self.highest.t2_child_rel, DictRelationship)

        assert self.highest.t1_child_rel.parent == self.highest.t1
        assert self.highest.t2_child_rel.parent == self.highest.t2
        assert self.highest.t1_child_rel.parent == self.highest.t1
        assert self.highest.t2_child_rel.parent == self.highest.t2

        # Provides textual relationship from t1 to t1[1337]
        assert '[1337]' == self.highest.t2_child_rel.get_param_repr()

    def test_path(self):
        # Provides textual path all the way through
        assert self.lowest.path("self.t1") == "self.t1[1337].a"

    def test_path_output_list(self):
        # Provides textual path all the way through
        assert self.lowest.path(output_format="list") == [1337, 'a']

    def test_change_of_path_root(self):
        assert self.lowest.path("root") == "root[1337].a"
        assert self.lowest.path("") == "[1337].a"

    def test_path_when_both_children_empty(self):
        """
        This is a situation that should never happen.
        But we are creating it artificially.
        """
        t1 = {1: 1}
        t2 = {1: 2}
        child_t1 = {}
        child_t2 = {}
        up = DiffLevel(t1, t2)
        down = up.down = DiffLevel(child_t1, child_t2)
        path = down.path()
        assert path == 'root'
        assert down.path(output_format='list') == []

    def test_t2_path_when_nested(self):
        t1 = {
            "type": "struct",
            "fields": [
                {"name": "Competition", "metadata": {}, "nullable": True, "type": "string"},
                {"name": "TeamName", "metadata": {}, "nullable": True, "type": "string"},
                {
                    "name": "Contents",
                    "metadata": {},
                    "nullable": True,
                    "type": {
                        "type": "struct",
                        "fields": [
                            {"name": "Date", "metadata": {}, "nullable": True, "type": "string"},
                            {"name": "Player1", "metadata": {}, "nullable": True, "type": "string"}
                        ]
                    }
                }
            ]
        }

        t2 = {
            "type": "struct",
            "fields": [
                {"name": "Competition", "metadata": {}, "nullable": True, "type": "string"},
                {"name": "GlobalId", "metadata": {}, "nullable": True, "type": "string"},
                {"name": "TeamName", "metadata": {}, "nullable": True, "type": "string"},
                {
                    "name": "Contents",
                    "metadata": {},
                    "nullable": True,
                    "type": {
                        "type": "struct",
                        "fields": [
                            {"name": "Date", "metadata": {}, "nullable": True, "type": "string"},
                            {"name": "Player1", "metadata": {}, "nullable": True, "type": "string"},
                            {"name": "Player2", "metadata": {}, "nullable": True, "type": "string"}
                        ]
                    }
                }
            ]
        }

        diff = DeepDiff(t1=t1, t2=t2, ignore_order=True, verbose_level=2, view='tree')

        expected_diff = {
            "iterable_item_added": {
                "root['fields'][1]": {
                    "name": "GlobalId",
                    "metadata": {},
                    "nullable": True,
                    "type": "string",
                },
                "root['fields'][2]['type']['fields'][2]": {
                    "name": "Player2",
                    "metadata": {},
                    "nullable": True,
                    "type": "string",
                },
            }
        }

        path = diff['iterable_item_added'][1].path()
        assert "root['fields'][2]['type']['fields'][2]" == path

        path_t2 = diff['iterable_item_added'][1].path(use_t2=True)
        assert "root['fields'][3]['type']['fields'][2]" == path_t2



    def test_repr_short(self):
        level = self.lowest.verbose_level
        try:
            self.lowest.verbose_level = 0
            item_repr = repr(self.lowest)
        finally:
            self.lowest.verbose_level = level
        assert item_repr == '<root[1337].a>'

    def test_repr_long(self):
        level = self.lowest.verbose_level
        try:
            self.lowest.verbose_level = 1
            item_repr = repr(self.lowest)
        finally:
            self.lowest.verbose_level = level
        assert item_repr == "<root[1337].a t1:'very long t...', t2:313>"

    def test_repr_very_long(self):
        level = self.lowest.verbose_level
        try:
            self.lowest.verbose_level = 2
            item_repr = repr(self.lowest)
        finally:
            self.lowest.verbose_level = level
        assert item_repr == "<root[1337].a t1:'very long t...', t2:313>"

    def test_repetition_attribute_and_repr(self):
        t1 = [1, 1]
        t2 = [1]
        some_repetition = 'some repetition'
        node = DiffLevel(t1, t2)
        node.additional['repetition'] = some_repetition
        assert node.repetition == some_repetition
        assert repr(node) == "<root {'repetition': 'some repetition'}>"


class TestChildRelationship:
    def test_create_invalid_klass(self):
        with pytest.raises(TypeError):
            ChildRelationship.create(DiffLevel, "hello", 42)

    def test_rel_repr_short(self):
        rel = WorkingChildRelationship(parent="that parent", child="this child", param="some param")
        rel_repr = repr(rel)
        expected = "<WorkingChildRelationship parent:'that parent', child:'this child', param:'some param'>"
        assert rel_repr == expected

    def test_rel_repr_long(self):
        rel = WorkingChildRelationship(
            parent="that parent who has a long path",
            child="this child",
            param="some param")
        rel_repr = repr(rel)
        expected = "<WorkingChildRelationship parent:'that parent...', child:'this child', param:'some param'>"
        assert rel_repr == expected
