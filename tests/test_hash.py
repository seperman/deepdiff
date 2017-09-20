#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
To run only the search tests:
    python -m unittest tests.test_hash

Or to run all the tests:
    python -m unittest discover

Or to run all the tests with coverage:
    coverage run --source deepdiff setup.py test

Or using Nose:
    nosetests --with-coverage --cover-package=deepdiff

To run a specific test, run this from the root of repo:
    On linux:
    nosetests ./tests/test_hash.py:DeepHashTestCase.test_bytecode

    On windows:
    nosetests .\tests\test_hash.py:DeepHashTestCase.test_string_in_root
"""
import unittest
from deepdiff import DeepHash
from deepdiff.helper import py3, pypy3
from collections import namedtuple
from functools import partial
import logging

logging.disable(logging.CRITICAL)


class CustomClass:
    def __init__(self, a, b=None):
        self.a = a
        self.b = b

    def __str__(self):
        return "({}, {})".format(self.a, self.b)

    def __repr__(self):
        return self.__str__()


hasher = DeepHash(None).hasher
# Only the prep part of DeepHashPrep. We don't need to test the actual hash function.
DeepHashPrep = partial(DeepHash, constant_size=False)


def prep_str(obj):
    return 'str:{}'.format(obj)


class DeepHashTestCase(unittest.TestCase):
    """DeepHashPrep Tests."""

    def test_prep_str(self):
        obj = "a"
        expected_result = {id(obj): prep_str(obj)}
        result = DeepHashPrep(obj)
        self.assertEqual(result, expected_result)

    def test_prep_str_fail_if_mutable(self):
        """
        This test fails if ContentHash is getting a mutable copy of hashes
        which means each init of the ContentHash will have hashes from
        the previous init.
        """
        obj1 = "a"
        id_obj1 = id(obj1)
        expected_result = {id_obj1: prep_str(obj1)}
        result = DeepHashPrep(obj1)
        self.assertEqual(result, expected_result)
        obj2 = "b"
        result = DeepHashPrep(obj2)
        self.assertTrue(id_obj1 not in result)

    def do_list_or_tuple(self, func, func_str):
        string1 = "a"
        obj = func([string1, 10, 20])
        string1_prepped = prep_str(string1)
        expected_result = {
            id(string1): string1_prepped,
            id(obj): '{}:int:10,int:20,{}'.format(func_str, string1_prepped),
            id(10): 'int:10',
            id(20): 'int:20'
        }
        result = DeepHashPrep(obj)
        self.assertEqual(result, expected_result)

    def test_list_and_tuple(self):
        for func, func_str in ((list, 'list'), (tuple, 'tuple')):
            self.do_list_or_tuple(func, func_str)

    def test_named_tuples(self):
        # checking if pypy3 is running the test
        # in that case due to a pypy3 bug or something
        # the id of x inside the named tuple changes.
        x = "x"
        x_id = id(x)
        x_prep = prep_str(x)
        Point = namedtuple('Point', [x])
        obj = Point(x=11)
        result = DeepHashPrep(obj)
        if pypy3:
            self.assertEqual(result[id(obj)], 'ntdict:{str:%s:int:11}' % x)
        else:
            expected_result = {
                x_id: x_prep,
                id(obj): 'ntdict:{str:%s:int:11}' % x,
                id(11): 'int:11',
            }
            self.assertEqual(result, expected_result)

    def test_dict(self):
        string1 = "a"
        string1_prepped = prep_str(string1)
        key1 = "key1"
        key1_prepped = prep_str(key1)
        obj = {key1: string1, 1: 10, 2: 20}
        expected_result = {
            id(1): "int:1",
            id(2): "int:2",
            id(10): "int:10",
            id(20): "int:20",
            id(key1): key1_prepped,
            id(string1): string1_prepped,
            id(obj): 'dict:{int:1:int:10;int:2:int:20;str:%s:str:%s}' % (key1, string1)
        }
        result = DeepHashPrep(obj)
        self.assertEqual(result, expected_result)

    def test_dict_in_list(self):
        string1 = "a"
        hash_string1 = hash(string1)
        key1 = "key1"
        hash_key1 = hash(key1)
        dict1 = {key1: string1, 1: 10, 2: 20}
        obj = [0, dict1]
        expected_result = {
            id(key1): "str:{}".format(hash_key1),
            id(string1): "str:{}".format(hash_string1),
            id(dict1): 'dict:{int:1:int:10;int:2:int:20;str:%s:str:%s}' %
            (hash_key1, hash_string1),
            id(obj):
            'list:dict:{int:1:int:10;int:2:int:20;str:%s:str:%s},int:0' %
            (hash_key1, hash_string1)
        }
        result = DeepHashPrep(obj)
        self.assertEqual(result, expected_result)

    def test_nested_lists_same_hash(self):
        t1 = [1, 2, [3, 4]]
        t2 = [[4, 3], 2, 1]
        t1_hash = DeepHashPrep(t1)
        t2_hash = DeepHashPrep(t2)

        self.assertEqual(t1_hash[id(t1)], t2_hash[id(t2)])

    def test_nested_lists_same_hash2(self):
        t1 = [1, 2, [3, [4, 5]]]
        t2 = [[[5, 4], 3], 2, 1]
        t1_hash = DeepHashPrep(t1)
        t2_hash = DeepHashPrep(t2)

        self.assertEqual(t1_hash[id(t1)], t2_hash[id(t2)])

    def test_nested_lists_same_hash3(self):
        t1 = [{1: [2, 3], 4: [5, [6, 7]]}]
        t2 = [{4: [[7, 6], 5], 1: [3, 2]}]
        t1_hash = DeepHashPrep(t1)
        t2_hash = DeepHashPrep(t2)

        self.assertEqual(t1_hash[id(t1)], t2_hash[id(t2)])

    def test_nested_lists_in_dictionary_same_hash(self):
        t1 = [{"c": 4}, {"c": 3}]
        t2 = [{"c": 3}, {"c": 4}]
        t1_hash = DeepHashPrep(t1)
        t2_hash = DeepHashPrep(t2)

        self.assertEqual(t1_hash[id(t1)], t2_hash[id(t2)])

    def test_same_sets_same_hash(self):
        t1 = {1, 3, 2}
        t2 = {2, 3, 1}
        t1_hash = DeepHashPrep(t1)
        t2_hash = DeepHashPrep(t2)

        self.assertEqual(t1_hash[id(t1)], t2_hash[id(t2)])

    def test_same_sets_in_lists_same_hash(self):
        t1 = ["a", {1, 3, 2}]
        t2 = [{2, 3, 1}, "a"]
        t1_hash = DeepHashPrep(t1)
        t2_hash = DeepHashPrep(t2)

        self.assertEqual(t1_hash[id(t1)], t2_hash[id(t2)])

    def test_unknown_parameters(self):
        with self.assertRaises(ValueError):
            DeepHashPrep(1, wrong_param=2)

    def test_bad_attribute(self):
        class Bad(object):
            __slots__ = ['x', 'y']

            def __getattr__(self, key):
                raise AttributeError("Bad item")

            def __str__(self):
                return "Bad Object"

        t1 = Bad()

        result = DeepHashPrep(t1)
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

        hash_a = DeepHashPrep(a)
        hash_b = DeepHashPrep(b)

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

        hash_a = DeepHashPrep(a, ignore_repetition=False)
        hash_b = DeepHashPrep(b, ignore_repetition=False)

        self.assertNotEqual(hash_a[list1_id], hash_b[list2_id])
        self.assertNotEqual(hash_a[a_id], hash_b[b_id])

        self.assertEqual(hash_a[list1_id].replace('3|1', '3|2'),
                         hash_b[list2_id])

    def test_already_calculated_hash_wont_be_recalculated(self):
        hashes = (i for i in range(10))

        def hasher(obj):
            return next(hashes)

        obj = "a"
        expected_result = {id(obj): "str:0"}
        result = DeepHashPrep(obj, hasher=hasher)
        self.assertEqual(result, expected_result)

        # we simply feed the last result to DeepHashPrep
        # So it can re-use the results.
        result2 = DeepHashPrep(obj, hasher=hasher, hashes=result)
        # if hashes are not cached and re-used,
        # then the next time hasher runs, it returns
        # number 1 instead of 0.
        self.assertEqual(result2, expected_result)

        result3 = DeepHashPrep(obj, hasher=hasher)
        expected_result = {id(obj): "str:{}".format(1)}
        self.assertEqual(result3, expected_result)

    def test_skip_type(self):
        l1 = logging.getLogger("test")
        obj = {"log": l1, 2: 1337}
        result = DeepHashPrep(obj, exclude_types={logging.Logger})
        self.assertEqual(result[id(l1)], result.skipped)

    def test_prep_dic_with_loop(self):
        obj = {2: 1337}
        obj[1] = obj
        result = DeepHashPrep(obj)
        expected_result = {id(obj): 'dict:{int:2:int:1337}'}
        self.assertEqual(result, expected_result)

    def test_prep_iterable_with_loop(self):
        obj = [1]
        obj.append(obj)
        result = DeepHashPrep(obj)
        expected_result = {id(obj): 'list:int:1'}
        self.assertEqual(result, expected_result)

    def test_prep_iterable_with_excluded_type(self):
        l1 = logging.getLogger("test")
        obj = [1, l1]
        result = DeepHashPrep(obj, exclude_types={logging.Logger})
        self.assertTrue(id(l1) not in result)


class DeepHashSHA1TestCase(unittest.TestCase):
    """DeepHashPrep with SHA1 Tests."""

    def test_prep_str(self):
        obj = "a"
        expected_result = {
            id(obj): 'str:48591f1d794734cabf55f96f5a5a72c084f13ac0'
        }
        result = DeepHashPrep(obj, hasher=DeepHashPrep.sha1hex)
        self.assertEqual(result, expected_result)

    def test_prep_str_fail_if_mutable(self):
        """
        This test fails if ContentHash is getting a mutable copy of hashes
        which means each init of the ContentHash will have hashes from
        the previous init.
        """
        obj1 = "a"
        id_obj1 = id(obj1)
        expected_result = {
            id_obj1: 'str:48591f1d794734cabf55f96f5a5a72c084f13ac0'
        }
        result = DeepHashPrep(obj1, hasher=DeepHashPrep.sha1hex)
        self.assertEqual(result, expected_result)
        obj2 = "b"
        result = DeepHashPrep(obj2, hasher=DeepHashPrep.sha1hex)
        self.assertTrue(id_obj1 not in result)

    def test_bytecode(self):
        obj = b"a"
        if py3:
            expected_result = {
                id(obj): 'str:066c7cf4158717c47244fa6cf1caafca605d550b'
            }
        else:
            expected_result = {
                id(obj): 'str:48591f1d794734cabf55f96f5a5a72c084f13ac0'
            }
        result = DeepHashPrep(obj, hasher=DeepHashPrep.sha1hex)
        self.assertEqual(result, expected_result)

    def test_list1(self):
        string1 = "a"
        obj = [string1, 10, 20]
        expected_result = {
            id(string1): 'str:48591f1d794734cabf55f96f5a5a72c084f13ac0',
            id(obj):
            'list:int:10,int:20,str:48591f1d794734cabf55f96f5a5a72c084f13ac0'
        }
        result = DeepHashPrep(obj, hasher=DeepHashPrep.sha1hex)
        self.assertEqual(result, expected_result)

    def test_dict1(self):
        string1 = "a"
        key1 = "key1"
        obj = {key1: string1, 1: 10, 2: 20}
        expected_result = {
            id(key1): 'str:63216212fdf88fe0c838c36ab65278b9953000d6',
            id(string1): 'str:48591f1d794734cabf55f96f5a5a72c084f13ac0',
            id(obj):
            'dict:{int:1:int:10;int:2:int:20;str:63216212fdf88fe0c838c36ab65278b9953000d6:str:48591f1d794734cabf55f96f5a5a72c084f13ac0}'
        }
        result = DeepHashPrep(obj, hasher=DeepHashPrep.sha1hex)
        self.assertEqual(result, expected_result)
