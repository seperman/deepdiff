#!/usr/bin/env python
import uuid
import unittest
from deepdiff import DeepDiff


class TestIgnoreUuidTypes(unittest.TestCase):
    """Test ignore_uuid_types functionality"""

    def test_uuid_vs_string_without_ignore(self):
        """Test that UUID vs string reports type change by default"""
        test_uuid = uuid.UUID('12345678-1234-5678-1234-567812345678')
        uuid_str = '12345678-1234-5678-1234-567812345678'
        
        result = DeepDiff(test_uuid, uuid_str)
        
        assert 'type_changes' in result
        assert result['type_changes']['root']['old_type'] == uuid.UUID
        assert result['type_changes']['root']['new_type'] == str
        assert result['type_changes']['root']['old_value'] == test_uuid
        assert result['type_changes']['root']['new_value'] == uuid_str

    def test_uuid_vs_string_with_ignore(self):
        """Test that UUID vs string is ignored when ignore_uuid_types=True"""
        test_uuid = uuid.UUID('12345678-1234-5678-1234-567812345678')
        uuid_str = '12345678-1234-5678-1234-567812345678'
        
        result = DeepDiff(test_uuid, uuid_str, ignore_uuid_types=True)
        
        assert result == {}

    def test_string_vs_uuid_with_ignore(self):
        """Test that string vs UUID is ignored when ignore_uuid_types=True (reverse order)"""
        test_uuid = uuid.UUID('12345678-1234-5678-1234-567812345678')
        uuid_str = '12345678-1234-5678-1234-567812345678'
        
        result = DeepDiff(uuid_str, test_uuid, ignore_uuid_types=True)
        
        assert result == {}

    def test_different_uuid_values_with_ignore(self):
        """Test that different UUID values are still reported"""
        uuid1 = uuid.UUID('12345678-1234-5678-1234-567812345678')
        uuid2 = uuid.UUID('87654321-4321-8765-4321-876543218765')
        
        result = DeepDiff(uuid1, uuid2, ignore_uuid_types=True)
        
        assert 'values_changed' in result
        assert result['values_changed']['root']['old_value'] == uuid1
        assert result['values_changed']['root']['new_value'] == uuid2

    def test_uuid_vs_different_string_with_ignore(self):
        """Test that UUID vs different UUID string reports value change"""
        test_uuid = uuid.UUID('12345678-1234-5678-1234-567812345678')
        different_str = '87654321-4321-8765-4321-876543218765'
        
        result = DeepDiff(test_uuid, different_str, ignore_uuid_types=True)
        
        assert 'values_changed' in result
        assert result['values_changed']['root']['old_value'] == test_uuid
        assert result['values_changed']['root']['new_value'] == different_str

    def test_uuid_vs_invalid_string_with_ignore(self):
        """Test that UUID vs invalid UUID string reports value change"""
        test_uuid = uuid.UUID('12345678-1234-5678-1234-567812345678')
        invalid_str = 'not-a-uuid'
        
        result = DeepDiff(test_uuid, invalid_str, ignore_uuid_types=True)
        
        assert 'values_changed' in result
        assert result['values_changed']['root']['old_value'] == test_uuid
        assert result['values_changed']['root']['new_value'] == invalid_str

    def test_uuid_in_dict_with_ignore(self):
        """Test that UUID vs string in dictionaries works correctly"""
        test_uuid = uuid.UUID('12345678-1234-5678-1234-567812345678')
        uuid_str = '12345678-1234-5678-1234-567812345678'
        
        dict1 = {'id': test_uuid, 'name': 'test', 'count': 42}
        dict2 = {'id': uuid_str, 'name': 'test', 'count': 42}
        
        result = DeepDiff(dict1, dict2, ignore_uuid_types=True)
        
        assert result == {}

    def test_uuid_in_list_with_ignore(self):
        """Test that UUID vs string in lists works correctly"""
        test_uuid = uuid.UUID('12345678-1234-5678-1234-567812345678')
        uuid_str = '12345678-1234-5678-1234-567812345678'
        
        list1 = [test_uuid, 'test', 42]
        list2 = [uuid_str, 'test', 42]
        
        result = DeepDiff(list1, list2, ignore_uuid_types=True)
        
        assert result == {}

    def test_mixed_uuid_comparisons_with_ignore(self):
        """Test mixed UUID/string comparisons in nested structures"""
        uuid1 = uuid.UUID('12345678-1234-5678-1234-567812345678')
        uuid2 = uuid.UUID('87654321-4321-8765-4321-876543218765')
        
        data1 = {
            'uuid_obj': uuid1,
            'uuid_str': '12345678-1234-5678-1234-567812345678',
            'nested': {
                'id': uuid2,
                'items': [uuid1, 'test']
            }
        }
        
        data2 = {
            'uuid_obj': '12345678-1234-5678-1234-567812345678',  # string version
            'uuid_str': uuid1,  # UUID object version
            'nested': {
                'id': '87654321-4321-8765-4321-876543218765',  # string version
                'items': ['12345678-1234-5678-1234-567812345678', 'test']  # string version
            }
        }
        
        result = DeepDiff(data1, data2, ignore_uuid_types=True)
        
        assert result == {}

    def test_uuid_with_other_ignore_flags(self):
        """Test that ignore_uuid_types works with other ignore flags"""
        test_uuid = uuid.UUID('12345678-1234-5678-1234-567812345678')
        
        data1 = {
            'id': test_uuid,
            'name': 'TEST',
            'count': 42
        }
        
        data2 = {
            'id': '12345678-1234-5678-1234-567812345678',
            'name': 'test',  # different case
            'count': 42.0  # different numeric type
        }
        
        result = DeepDiff(data1, data2, 
                         ignore_uuid_types=True,
                         ignore_string_case=True,
                         ignore_numeric_type_changes=True)
        
        assert result == {}


if __name__ == '__main__':
    unittest.main()