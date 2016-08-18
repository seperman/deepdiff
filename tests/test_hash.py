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
    On linux:
    nosetests ./tests/hash_tests.py:DeepHashTestCase.test_bytecode

    On windows:
    nosetests .\tests\hash_tests.py:DeepHashTestCase.test_string_in_root
"""
import unittest
from deepdiff import DeepHash
import sys
from sys import version
from collections import namedtuple
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
    """DeepHash Tests."""

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

    def test_list(self):
        string1 = "a"
        obj = [string1, 10, 20]
        expected_result = {id(string1): hash(string1),
                           id(obj): 'list:int:10,int:20,str:%s' % hash(string1)}
        result = DeepHash(obj)
        self.assertEqual(result, expected_result)

    def test_tuple(self):
        string1 = "a"
        obj = (string1, 10, 20)
        expected_result = {id(string1): hash(string1),
                           id(obj): 'tuple:int:10,int:20,str:%s' % hash(string1)}
        result = DeepHash(obj)
        self.assertEqual(result, expected_result)

    def test_named_tuples(self):
        # checking if pypy3 is running the test
        # in that case due to a pypy3 bug or something
        # the id of x inside the named tuple changes.
        x = "x"
        x_id = id(x)
        x_hash = hash(x)
        Point = namedtuple('Point', [x])
        obj = Point(x=11)
        result = DeepHash(obj)
        if py3 and hasattr(sys, "pypy_translation_info"):
            self.assertEqual(result[id(obj)], 'ntdict:{str:%s:int:11}' % x_hash)
        else:
            expected_result = {x_id: x_hash, id(obj): 'ntdict:{str:%s:int:11}' % x_hash}
            self.assertEqual(result, expected_result)

    def test_dict(self):
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

        result = DeepHash(t1)
        expected_result = {id(t1): result.unprocessed, 'unprocessed': [t1]}
        self.assertEqual(result, expected_result)

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

    def test_setting_repetition_off_unequal_hash(self):
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

    def test_already_calculated_hash_wont_be_recalculated(self):
        hashes = (i for i in range(10))

        def hasher(obj):
            return next(hashes)

        obj = "a"
        expected_result = {id(obj): 0}
        result = DeepHash(obj, hasher=hasher)
        self.assertEqual(result, expected_result)

        # we simply feed the last result to DeepHash
        # So it can re-use the results.
        result2 = DeepHash(obj, hasher=hasher, hashes=result)
        # if hashes are not cached and re-used,
        # then the next time hasher runs, it returns
        # number 1 instead of 0.
        self.assertEqual(result2, expected_result)

        result3 = DeepHash(obj, hasher=hasher)
        expected_result = {id(obj): 1}
        self.assertEqual(result3, expected_result)

    def test_skip_type(self):
        l1 = logging.getLogger("test")
        obj = {"log": l1, 2: 1337}
        result = DeepHash(obj, exclude_types={logging.Logger})
        self.assertEqual(result[id(l1)], result.skipped)

    def test_hash_dic_with_loop(self):
        obj = {2: 1337}
        obj[1] = obj
        result = DeepHash(obj)
        expected_result = {id(obj): 'dict:{int:2:int:1337}'}
        self.assertEqual(result, expected_result)

    def test_hash_iterable_with_loop(self):
        obj = [1]
        obj.append(obj)
        result = DeepHash(obj)
        expected_result = {id(obj): 'list:int:1'}
        self.assertEqual(result, expected_result)

    def test_hash_iterable_with_excluded_type(self):
        l1 = logging.getLogger("test")
        obj = [1, l1]
        result = DeepHash(obj, exclude_types={logging.Logger})
        self.assertTrue(id(l1) not in result)


class DeepHashSHA1TestCase(unittest.TestCase):
    """DeepHash with SHA1 Tests."""

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

    def test_bytecode(self):
        obj = b"a"
        if py3:
            expected_result = {id(obj): '066c7cf4158717c47244fa6cf1caafca605d550b'}
        else:
            expected_result = {id(obj): '48591f1d794734cabf55f96f5a5a72c084f13ac0'}
        result = DeepHash(obj, hasher=DeepHash.sha1hex)
        self.assertEqual(result, expected_result)

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
