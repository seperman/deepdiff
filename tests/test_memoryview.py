#!/usr/bin/env python
import pytest
from deepdiff import DeepDiff


class TestMemoryView:
    """Test memoryview support in DeepDiff"""

    def test_memoryview_basic_comparison(self):
        """Test basic memoryview comparison without ignore_string_type_changes"""
        t1 = memoryview(b"hello")
        t2 = memoryview(b"world")
        
        diff = DeepDiff(t1, t2)
        assert 'values_changed' in diff
        assert diff['values_changed']['root']['old_value'] == t1
        assert diff['values_changed']['root']['new_value'] == t2
    
    def test_memoryview_with_bytes_type_change(self):
        """Test memoryview vs bytes comparison shows type change"""
        t1 = memoryview(b"hello")
        t2 = b"hello"
        
        diff = DeepDiff(t1, t2)
        assert 'type_changes' in diff
        assert diff['type_changes']['root']['old_type'] == memoryview
        assert diff['type_changes']['root']['new_type'] == bytes
        assert diff['type_changes']['root']['old_value'] == t1
        assert diff['type_changes']['root']['new_value'] == t2
    
    def test_memoryview_with_str_type_change(self):
        """Test memoryview vs str comparison shows type change"""
        t1 = memoryview(b"hello")
        t2 = "hello"
        
        diff = DeepDiff(t1, t2)
        assert 'type_changes' in diff
        assert diff['type_changes']['root']['old_type'] == memoryview
        assert diff['type_changes']['root']['new_type'] == str
        assert diff['type_changes']['root']['old_value'] == t1
        assert diff['type_changes']['root']['new_value'] == t2
    
    def test_memoryview_ignore_string_type_changes_with_bytes(self):
        """Test memoryview vs bytes with ignore_string_type_changes=True"""
        t1 = memoryview(b"hello")
        t2 = b"hello"
        
        diff = DeepDiff(t1, t2, ignore_string_type_changes=True)
        assert diff == {}
    
    def test_memoryview_ignore_string_type_changes_with_str(self):
        """Test memoryview vs str with ignore_string_type_changes=True"""
        t1 = memoryview(b"hello")
        t2 = "hello"
        
        diff = DeepDiff(t1, t2, ignore_string_type_changes=True)
        assert diff == {}
    
    def test_memoryview_different_content_with_ignore_string_type_changes(self):
        """Test memoryview with different content still shows value change"""
        t1 = memoryview(b"hello")
        t2 = "world"
        
        diff = DeepDiff(t1, t2, ignore_string_type_changes=True)
        assert 'values_changed' in diff
        # The values in the diff are the original objects, not converted strings
        assert diff['values_changed']['root']['old_value'] == t1
        assert diff['values_changed']['root']['new_value'] == t2
    
    def test_memoryview_in_dict_keys(self):
        """Test memoryview as dictionary keys"""
        t1 = {memoryview(b"key1"): "value1", memoryview(b"key2"): "value2"}
        t2 = {b"key1": "value1", "key2": "value2"}
        
        # Without ignore_string_type_changes, should show differences
        diff = DeepDiff(t1, t2)
        assert 'dictionary_item_removed' in diff or 'dictionary_item_added' in diff
        
        # With ignore_string_type_changes, should be equal
        diff = DeepDiff(t1, t2, ignore_string_type_changes=True)
        assert diff == {}
    
    def test_memoryview_in_list(self):
        """Test memoryview in lists"""
        t1 = [memoryview(b"hello"), memoryview(b"world")]
        t2 = ["hello", b"world"]
        
        diff = DeepDiff(t1, t2, ignore_string_type_changes=True)
        assert diff == {}
    
    def test_memoryview_in_nested_structure(self):
        """Test memoryview in nested structures"""
        t1 = {
            "data": {
                "items": [memoryview(b"item1"), memoryview(b"item2")],
                "metadata": {memoryview(b"key"): "value"}
            }
        }
        t2 = {
            "data": {
                "items": ["item1", b"item2"],
                "metadata": {"key": "value"}
            }
        }
        
        diff = DeepDiff(t1, t2, ignore_string_type_changes=True)
        assert diff == {}
    
    def test_memoryview_with_non_ascii_bytes(self):
        """Test memoryview with non-ASCII bytes"""
        t1 = memoryview(b"\x80\x81\x82")
        t2 = b"\x80\x81\x82"
        
        diff = DeepDiff(t1, t2, ignore_string_type_changes=True)
        assert diff == {}
    
    def test_memoryview_text_diff(self):
        """Test that text diff works with memoryview"""
        t1 = {"data": memoryview(b"hello\nworld")}
        t2 = {"data": memoryview(b"hello\nearth")}
        
        diff = DeepDiff(t1, t2)
        assert 'values_changed' in diff
        assert "root['data']" in diff['values_changed']
        # Should contain diff output
        assert 'diff' in diff['values_changed']["root['data']"]
    
    def test_memoryview_with_ignore_type_in_groups(self):
        """Test memoryview with ignore_type_in_groups parameter"""
        from deepdiff.helper import strings
        
        t1 = memoryview(b"hello")
        t2 = "hello"
        
        # Using ignore_type_in_groups with strings tuple
        diff = DeepDiff(t1, t2, ignore_type_in_groups=[strings])
        assert diff == {}
    
    def test_memoryview_hash(self):
        """Test that DeepHash works with memoryview"""
        from deepdiff import DeepHash
        
        # Test basic hashing
        obj1 = memoryview(b"hello")
        hash1 = DeepHash(obj1)
        assert hash1[obj1]
        
        # Test with ignore_string_type_changes
        obj2 = "hello"
        hash2 = DeepHash(obj2, ignore_string_type_changes=True)
        hash1_ignore = DeepHash(obj1, ignore_string_type_changes=True)
        
        # When ignoring string type changes, memoryview and str of same content should hash the same
        assert hash1_ignore[obj1] == hash2[obj2]