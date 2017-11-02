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


# Only the prep part of DeepHash. We don't need to test the actual hash function.
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
            id(10): 'int:10',
            id(20): 'int:20',
            id(string1): string1_prepped,
            id(obj): '{}:int:10,int:20,{}'.format(func_str, string1_prepped),
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
            id(1): 'int:1',
            id(10): 'int:10',
            id(2): 'int:2',
            id(20): 'int:20',
            id(key1): key1_prepped,
            id(string1): string1_prepped,
            id(obj): 'dict:{int:1:int:10;int:2:int:20;str:%s:str:%s}' % (key1, string1)
        }
        result = DeepHashPrep(obj)
        self.assertEqual(result, expected_result)

    def test_dict_in_list(self):
        string1 = "a"
        key1 = "key1"
        dict1 = {key1: string1, 1: 10, 2: 20}
        obj = [0, dict1]
        expected_result = {
            id(0): 'int:0',
            id(1): 'int:1',
            id(10): 'int:10',
            id(2): 'int:2',
            id(20): 'int:20',
            id(key1): "str:{}".format(key1),
            id(string1): "str:{}".format(string1),
            id(dict1): 'dict:{int:1:int:10;int:2:int:20;str:%s:str:%s}' %
            (key1, string1),
            id(obj):
            'list:dict:{int:1:int:10;int:2:int:20;str:%s:str:%s},int:0' %
            (key1, string1)
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

    def test_similar_sets_with_significant_digits_same_hash(self):
        t1 = {0.012, 0.98}
        t2 = {0.013, 0.99}
        t1_hash = DeepHashPrep(t1, significant_digits=1)
        t2_hash = DeepHashPrep(t2, significant_digits=1)

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
            return str(next(hashes))

        obj = "a"
        expected_result = {id(obj): '0'}
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
        expected_result = {id(obj): '1'}
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
        expected_result = {id(obj): 'dict:{int:2:int:1337}', id(1): 'int:1', id(2): 'int:2', id(1337): 'int:1337'}
        self.assertEqual(result, expected_result)

    def test_prep_iterable_with_loop(self):
        obj = [1]
        obj.append(obj)
        result = DeepHashPrep(obj)
        expected_result = {id(obj): 'list:int:1', id(1): 'int:1'}
        self.assertEqual(result, expected_result)

    def test_prep_iterable_with_excluded_type(self):
        l1 = logging.getLogger("test")
        obj = [1, l1]
        result = DeepHashPrep(obj, exclude_types={logging.Logger})
        self.assertTrue(id(l1) not in result)


class DeepHashSHA1TestCase(unittest.TestCase):
    """DeepHash with SHA1 Tests."""

    def test_prep_str(self):
        obj = "a"
        expected_result = {
            id(obj): 'c2a00c48d4713267a2ab9ca9739214127830e9be'
        }
        result = DeepHash(obj, hasher=DeepHash.sha1hex)
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
            id_obj1: 'c2a00c48d4713267a2ab9ca9739214127830e9be'
        }
        result = DeepHash(obj1, hasher=DeepHash.sha1hex)
        self.assertEqual(result, expected_result)
        obj2 = "b"
        result = DeepHash(obj2, hasher=DeepHash.sha1hex)
        self.assertTrue(id_obj1 not in result)

    def test_bytecode(self):
        obj = b"a"
        if py3:
            expected_result = {
                id(obj): '64a91ccb03c69f78d076d884de9bc5355849cc12'
            }
        else:
            expected_result = {
                id(obj): 'c2a00c48d4713267a2ab9ca9739214127830e9be'
            }
        result = DeepHash(obj, hasher=DeepHash.sha1hex)
        self.assertEqual(result, expected_result)

    def test_list1(self):
        string1 = "a"
        obj = [string1, 10, 20]
        expected_result = {
            id(string1): 'c2a00c48d4713267a2ab9ca9739214127830e9be',
            id(obj):
            '5af30c367e2e176f7c362356559f3e8cc73302e5',
            id(10): 'int:10',
            id(20): 'int:20',
        }
        result = DeepHash(obj, hasher=DeepHash.sha1hex)
        self.assertEqual(result, expected_result)

    def test_dict1(self):
        string1 = "a"
        key1 = "key1"
        obj = {key1: string1, 1: 10, 2: 20}
        expected_result = {
            id(1): 'int:1',
            id(10): 'int:10',
            id(2): 'int:2',
            id(20): 'int:20',
            id(key1): '35624f541de8d2cc9c31deba03c7dda9b1da09f7',
            id(string1): 'c2a00c48d4713267a2ab9ca9739214127830e9be',
            id(obj):
            'b13e2e23ed7e46208157e45bfbe0113782804e17'
        }
        result = DeepHash(obj, hasher=DeepHash.sha1hex)
        self.assertEqual(result, expected_result)
