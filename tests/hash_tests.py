#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
To run only the search tests:
    python -m unittest tests.hash_tests

Or to run all the tests with coverage:
    coverage run --source deepdiff setup.py test

Or using Nose:
    nosetests --with-coverage --cover-package=deepdiff

To run a specific test, run this from the root of repo:
    nosetests .\tests\hash_tests.py:DeepSearchTestCase.test_string_in_root
"""
import unittest
from deepdiff import DeepHash
from sys import version
import logging
logging.disable(logging.CRITICAL)

py3 = version[0] == '3'


class CustomClass:
    def __init__(self, a, b=None):
        self.a = a
        self.b = b

    def __str__(self):
        return "({}, {})".format(self.a, self.b)

    def __repr__(self):
        return self.__str__()


class DeepHashTestCase(unittest.TestCase):
    """DeepSearch Tests."""

    def test_hash_str(self):
        obj = "a"
        expected_result = {id(obj): hash(obj)}
        result = DeepHash(obj)
        self.assertEqual(result, expected_result)

    def test_hash_str_fail_if_mutable(self):
        """
        This test fails if ContentHash is getting a mutable copy of hashes
        which means each init of the ContentHash will have hashes from
        the previous init.
        """
        obj1 = "a"
        id_obj1 = id(obj1)
        expected_result = {id_obj1: hash(obj1)}
        result = DeepHash(obj1)
        self.assertEqual(result, expected_result)
        obj2 = "b"
        result = DeepHash(obj2)
        self.assertTrue(id_obj1 not in result)

    def test_list1(self):
        string1 = "a"
        obj = [string1, 10, 20]
        expected_result = {id(string1): hash(string1),
                           id(obj): 'list:int:10,int:20,str:%s' % hash(string1)}
        result = DeepHash(obj)
        self.assertEqual(result, expected_result)

    def test_dict1(self):
        string1 = "a"
        hash_string1 = hash(string1)
        key1 = "key1"
        hash_key1 = hash(key1)
        obj = {key1: string1, 1: 10, 2: 20}
        expected_result = {id(key1): hash_key1,
                           id(string1): hash_string1,
                           id(obj): 'dict:{int:1:int:10;int:2:int:20;str:%s:str:%s}' % (hash_key1, hash_string1)}
        result = DeepHash(obj)
        self.assertEqual(result, expected_result)

    def test_dict_in_list(self):
        string1 = "a"
        hash_string1 = hash(string1)
        key1 = "key1"
        hash_key1 = hash(key1)
        dict1 = {key1: string1, 1: 10, 2: 20}
        obj = [0, dict1]
        expected_result = {id(key1): hash_key1,
                           id(string1): hash_string1,
                           id(dict1): 'dict:{int:1:int:10;int:2:int:20;str:%s:str:%s}' % (hash_key1, hash_string1),
                           id(obj): 'list:dict:{int:1:int:10;int:2:int:20;str:%s:str:%s},int:0' % (hash_key1, hash_string1)}
        result = DeepHash(obj)
        self.assertEqual(result, expected_result)

    def test_nested_lists_same_hash(self):
        t1 = [1, 2, [3, 4]]
        t2 = [[4, 3], 2, 1]
        t1_hash = DeepHash(t1)
        t2_hash = DeepHash(t2)

        self.assertEqual(t1_hash[id(t1)], t2_hash[id(t2)])

    def test_nested_lists_same_hash2(self):
        t1 = [1, 2, [3, [4, 5]]]
        t2 = [[[5, 4], 3], 2, 1]
        t1_hash = DeepHash(t1)
        t2_hash = DeepHash(t2)

        self.assertEqual(t1_hash[id(t1)], t2_hash[id(t2)])

    def test_nested_lists_same_hash3(self):
        t1 = [{1: [2, 3], 4: [5, [6, 7]]}]
        t2 = [{4: [[7, 6], 5], 1: [3, 2]}]
        t1_hash = DeepHash(t1)
        t2_hash = DeepHash(t2)

        self.assertEqual(t1_hash[id(t1)], t2_hash[id(t2)])

    def test_same_sets_same_hash(self):
        t1 = {1, 3, 2}
        t2 = {2, 3, 1}
        t1_hash = DeepHash(t1)
        t2_hash = DeepHash(t2)

        self.assertEqual(t1_hash[id(t1)], t2_hash[id(t2)])

    def test_same_sets_in_lists_same_hash(self):
        t1 = ["a", {1, 3, 2}]
        t2 = [{2, 3, 1}, "a"]
        t1_hash = DeepHash(t1)
        t2_hash = DeepHash(t2)

        self.assertEqual(t1_hash[id(t1)], t2_hash[id(t2)])

    def test_unknown_parameters(self):
        with self.assertRaises(ValueError):
            DeepHash(1, wrong_param=2)

    def test_bad_attribute(self):
        class Bad(object):
            __slots__ = ['x', 'y']

            def __getattr__(self, key):
                raise AttributeError("Bad item")

            def __str__(self):
                return "Bad Object"

        t1 = Bad()

        ddiff = DeepHash(t1)
        result = {id(t1): DeepHash.Unprocessed, 'unprocessed': [t1]}
        self.assertEqual(ddiff, result)

    def test_repetition_by_default_does_not_effect(self):
        list1 = [3, 4]
        list1_id = id(list1)
        a = [1, 2, list1]
        a_id = id(a)

        list2 = [4, 3, 3]
        list2_id = id(list2)
        b = [list2, 2, 1]
        b_id = id(b)

        hash_a = DeepHash(a)
        hash_b = DeepHash(b)

        self.assertEqual(hash_a[list1_id], hash_b[list2_id])
        self.assertEqual(hash_a[a_id], hash_b[b_id])

    def test_repetition_off_affects_result(self):
        list1 = [3, 4]
        list1_id = id(list1)
        a = [1, 2, list1]
        a_id = id(a)

        list2 = [4, 3, 3]
        list2_id = id(list2)
        b = [list2, 2, 1]
        b_id = id(b)

        hash_a = DeepHash(a, ignore_repetition=False)
        hash_b = DeepHash(b, ignore_repetition=False)

        self.assertNotEqual(hash_a[list1_id], hash_b[list2_id])
        self.assertNotEqual(hash_a[a_id], hash_b[b_id])

        self.assertEqual(hash_a[list1_id].replace('3|1', '3|2'), hash_b[list2_id])


class DeepHashSHA1TestCase(unittest.TestCase):
    """DeepSearch Tests."""

    def test_hash_str(self):
        obj = "a"
        expected_result = {id(obj): '48591f1d794734cabf55f96f5a5a72c084f13ac0'}
        result = DeepHash(obj, hasher=DeepHash.sha1hex)
        self.assertEqual(result, expected_result)

    def test_hash_str_fail_if_mutable(self):
        """
        This test fails if ContentHash is getting a mutable copy of hashes
        which means each init of the ContentHash will have hashes from
        the previous init.
        """
        obj1 = "a"
        id_obj1 = id(obj1)
        expected_result = {id_obj1: '48591f1d794734cabf55f96f5a5a72c084f13ac0'}
        result = DeepHash(obj1, hasher=DeepHash.sha1hex)
        self.assertEqual(result, expected_result)
        obj2 = "b"
        result = DeepHash(obj2, hasher=DeepHash.sha1hex)
        self.assertTrue(id_obj1 not in result)

    def test_list1(self):
        string1 = "a"
        obj = [string1, 10, 20]
        expected_result = {id(string1): '48591f1d794734cabf55f96f5a5a72c084f13ac0',
                           id(obj): 'list:int:10,int:20,str:48591f1d794734cabf55f96f5a5a72c084f13ac0'}
        result = DeepHash(obj, hasher=DeepHash.sha1hex)
        self.assertEqual(result, expected_result)

    def test_dict1(self):
        string1 = "a"
        key1 = "key1"
        obj = {key1: string1, 1: 10, 2: 20}
        expected_result = {id(key1): '63216212fdf88fe0c838c36ab65278b9953000d6',
                           id(string1): '48591f1d794734cabf55f96f5a5a72c084f13ac0',
                           id(obj): 'dict:{int:1:int:10;int:2:int:20;str:63216212fdf88fe0c838c36ab65278b9953000d6:str:48591f1d794734cabf55f96f5a5a72c084f13ac0}'}
        result = DeepHash(obj, hasher=DeepHash.sha1hex)
        self.assertEqual(result, expected_result)
