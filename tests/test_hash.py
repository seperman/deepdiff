#!/usr/bin/env python
import re
import pytest
import logging
from deepdiff import DeepHash
from deepdiff.deephash import prepare_string_for_hashing, unprocessed, BoolObj
from deepdiff.helper import pypy3, get_id, number_to_string
from collections import namedtuple
from functools import partial
from enum import Enum

logging.disable(logging.CRITICAL)


class ClassC:
    class_attr = 0

    def __init__(self, a, b=None):
        self.a = a
        self.b = b

    def __str__(self):
        return "({}, {})".format(self.a, self.b)

    __repr__ = __str__


# Only the prep part of DeepHash. We don't need to test the actual hash function.
DeepHashPrep = partial(DeepHash, apply_hash=False)


def prep_str(obj, ignore_string_type_changes=True):
    return obj if ignore_string_type_changes else 'str:{}'.format(obj)


class TestDeepHash:

    def test_dictionary(self):

        obj = {1: 1}
        result = DeepHash(obj)
        assert set(result.keys()) == {1, get_id(obj)}

    def test_get_hash_by_obj_is_the_same_as_by_obj_get_id(self):
        a = "a"
        obj = {1: a}
        result = DeepHash(obj)
        assert result[a]

    def test_get_hash_by_obj_when_does_not_exist(self):
        a = "a"
        obj = {1: a}
        result = DeepHash(obj)
        with pytest.raises(KeyError):
            result[2]

    def test_list_of_sets(self):
        a = {1}
        b = {2}
        obj = [a, b]
        result = DeepHash(obj)
        expected_result = {1, 2, get_id(a), get_id(b), get_id(obj)}
        assert set(result.keys()) == expected_result

    def test_bad_attribute(self):
        class Bad:
            __slots__ = ['x', 'y']

            def __getattr__(self, key):
                raise AttributeError("Bad item")

            def __str__(self):
                return "Bad Object"

        t1 = Bad()

        result = DeepHash(t1)
        expected_result = {t1: unprocessed, 'unprocessed': [t1]}
        assert expected_result == result

    def test_built_in_hash_not_sensitive_to_bytecode_vs_unicode(self):
        a = 'hello'
        b = b'hello'
        a_hash = DeepHash(a, ignore_string_type_changes=True)[a]
        b_hash = DeepHash(b, ignore_string_type_changes=True)[b]
        assert a_hash == b_hash

    def test_sha1_hash_not_sensitive_to_bytecode_vs_unicode(self):
        a = 'hello'
        b = b'hello'
        a_hash = DeepHash(a, ignore_string_type_changes=True, hasher=DeepHash.sha1hex)[a]
        b_hash = DeepHash(b, ignore_string_type_changes=True, hasher=DeepHash.sha1hex)[b]
        assert a_hash == b_hash


class TestDeepHashPrep:
    """DeepHashPrep Tests covering object serialization."""

    def test_prep_bool_vs_num1(self):
        assert {BoolObj.TRUE: 'bool:true'} == DeepHashPrep(True)
        assert {1: 'int:1'} == DeepHashPrep(1)

    def test_prep_bool_vs_num2(self):
        item1 = {
            "Value One": True,
            "Value Two": 1,
        }
        item2 = {
            "Value Two": 1,
            "Value One": True,
        }
        assert DeepHashPrep(item1)[item1] == DeepHashPrep(item2)[item2]

    def test_prep_str(self):
        obj = "a"
        expected_result = {obj: prep_str(obj)}
        result = DeepHashPrep(obj, ignore_string_type_changes=True)
        assert expected_result == result
        expected_result = {obj: prep_str(obj, ignore_string_type_changes=False)}
        result = DeepHashPrep(obj, ignore_string_type_changes=False)
        assert expected_result == result

    def test_dictionary_key_type_change(self):
        obj1 = {"b": 10}
        obj2 = {b"b": 10}

        result1 = DeepHashPrep(obj1, ignore_string_type_changes=True)
        result2 = DeepHashPrep(obj2, ignore_string_type_changes=True)
        assert result1[obj1] == result2[obj2]
        assert result1["b"] == result2[b"b"]

    def test_number_type_change(self):
        obj1 = 10
        obj2 = 10.0

        result1 = DeepHashPrep(obj1)
        result2 = DeepHashPrep(obj2)
        assert result1[obj1] != result2[obj2]

        result1 = DeepHashPrep(obj1, ignore_numeric_type_changes=True)
        result2 = DeepHashPrep(obj2, ignore_numeric_type_changes=True)
        assert result1[obj1] == result2[obj2]

    def test_prep_str_fail_if_deephash_leaks_results(self):
        """
        This test fails if DeepHash is getting a mutable copy of hashes
        which means each init of the DeepHash will have hashes from
        the previous init.
        """
        obj1 = "a"
        expected_result = {obj1: prep_str(obj1)}
        result = DeepHashPrep(obj1, ignore_string_type_changes=True)
        assert expected_result == result
        obj2 = "b"
        result = DeepHashPrep(obj2, ignore_string_type_changes=True)
        assert obj1 not in result

    def test_dict_in_dict(self):
        obj2 = {2: 3}
        obj = {'a': obj2}
        result = DeepHashPrep(obj, ignore_string_type_changes=True)
        assert 'a' in result
        assert obj2 in result

    def do_list_or_tuple(self, func, func_str):
        string1 = "a"
        obj = func([string1, 10, 20])
        if func is list:
            obj_id = get_id(obj)
        else:
            obj_id = obj
        string1_prepped = prep_str(string1)
        expected_result = {
            10: 'int:10',
            20: 'int:20',
            string1: string1_prepped,
            obj_id: '{}:{},int:10,int:20'.format(func_str, string1_prepped),
        }
        result = DeepHashPrep(obj, ignore_string_type_changes=True)
        assert expected_result == result

    def test_list_and_tuple(self):
        for func, func_str in ((list, 'list'), (tuple, 'tuple')):
            self.do_list_or_tuple(func, func_str)

    def test_named_tuples(self):
        # checking if pypy3 is running the test
        # in that case due to a difference of string interning implementation
        # the id of x inside the named tuple changes.
        x = "x"
        x_prep = prep_str(x)
        Point = namedtuple('Point', [x])
        obj = Point(x=11)
        result = DeepHashPrep(obj, ignore_string_type_changes=True)
        if pypy3:
            assert result[obj] == "ntPoint:{%s:int:11}" % x
        else:
            expected_result = {
                x: x_prep,
                obj: "ntPoint:{%s:int:11}" % x,
                11: 'int:11',
            }
            assert expected_result == result

    def test_enum(self):
        class MyEnum(Enum):
            A = 1
            B = 2

        assert DeepHashPrep(MyEnum.A)[MyEnum.A] == r'objMyEnum:{str:_name_:str:A;str:_value_:int:1}'
        assert DeepHashPrep(MyEnum.A) == DeepHashPrep(MyEnum(1))
        assert DeepHashPrep(MyEnum.A) != DeepHashPrep(MyEnum.A.name)
        assert DeepHashPrep(MyEnum.A) != DeepHashPrep(MyEnum.A.value)
        assert DeepHashPrep(MyEnum.A) != DeepHashPrep(MyEnum.B)

    def test_dict_hash(self):
        string1 = "a"
        string1_prepped = prep_str(string1)
        key1 = "key1"
        key1_prepped = prep_str(key1)
        obj = {key1: string1, 1: 10, 2: 20}
        expected_result = {
            1: 'int:1',
            10: 'int:10',
            2: 'int:2',
            20: 'int:20',
            key1: key1_prepped,
            string1: string1_prepped,
            get_id(obj): 'dict:{{int:1:int:10;int:2:int:20;{}:{}}}'.format(key1, string1)
        }
        result = DeepHashPrep(obj, ignore_string_type_changes=True)
        assert expected_result == result

    def test_dict_in_list(self):
        string1 = "a"
        key1 = "key1"
        dict1 = {key1: string1, 1: 10, 2: 20}
        obj = [0, dict1]
        expected_result = {
            0: 'int:0',
            1: 'int:1',
            10: 'int:10',
            2: 'int:2',
            20: 'int:20',
            key1: key1,
            string1: string1,
            get_id(dict1): 'dict:{int:1:int:10;int:2:int:20;%s:%s}' %
            (key1, string1),
            get_id(obj):
            'list:dict:{int:1:int:10;int:2:int:20;%s:%s},int:0' %
            (key1, string1)
        }
        result = DeepHashPrep(obj, ignore_string_type_changes=True)
        assert expected_result == result

    def test_nested_lists_same_hash(self):
        t1 = [1, 2, [3, 4]]
        t2 = [[4, 3], 2, 1]
        t1_hash = DeepHashPrep(t1)
        t2_hash = DeepHashPrep(t2)

        assert t1_hash[get_id(t1)] == t2_hash[get_id(t2)]

    def test_nested_lists_same_hash2(self):
        t1 = [1, 2, [3, [4, 5]]]
        t2 = [[[5, 4], 3], 2, 1]
        t1_hash = DeepHashPrep(t1)
        t2_hash = DeepHashPrep(t2)

        assert t1_hash[get_id(t1)] == t2_hash[get_id(t2)]

    def test_nested_lists_same_hash3(self):
        t1 = [{1: [2, 3], 4: [5, [6, 7]]}]
        t2 = [{4: [[7, 6], 5], 1: [3, 2]}]
        t1_hash = DeepHashPrep(t1)
        t2_hash = DeepHashPrep(t2)

        assert t1_hash[get_id(t1)] == t2_hash[get_id(t2)]

    def test_nested_lists_in_dictionary_same_hash(self):
        t1 = [{"c": 4}, {"c": 3}]
        t2 = [{"c": 3}, {"c": 4}]
        t1_hash = DeepHashPrep(t1)
        t2_hash = DeepHashPrep(t2)

        assert t1_hash[get_id(t1)] == t2_hash[get_id(t2)]

    def test_same_sets_same_hash(self):
        t1 = {1, 3, 2}
        t2 = {2, 3, 1}
        t1_hash = DeepHashPrep(t1)
        t2_hash = DeepHashPrep(t2)

        assert t1_hash[get_id(t1)] == t2_hash[get_id(t2)]

    @pytest.mark.parametrize("t1, t2, significant_digits, number_format_notation, result", [
        ({0.012, 0.98}, {0.013, 0.99}, 1, "f", 'set:float:0.00,float:1.0'),
        (100000, 100021, 3, "e", 'int:1.000e+05'),
    ])
    def test_similar_significant_hash(self, t1, t2, significant_digits,
                                      number_format_notation, result):
        t1_hash = DeepHashPrep(t1, significant_digits=significant_digits,
                               number_format_notation=number_format_notation)
        t2_hash = DeepHashPrep(t2, significant_digits=significant_digits,
                               number_format_notation=number_format_notation)

        if result:
            assert result == t1_hash[t1] == t2_hash[t2]
        else:
            assert t1_hash[t1] != t2_hash[t2]

    def test_number_to_string_func(self):
        def custom_number_to_string(number, *args, **kwargs):
            number = 100 if number < 100 else number
            return number_to_string(number, *args, **kwargs)

        t1 = [10, 12, 100000]
        t2 = [50, 63, 100021]
        t1_hash = DeepHashPrep(t1, significant_digits=4, number_format_notation="e",
                               number_to_string_func=custom_number_to_string)
        t2_hash = DeepHashPrep(t2, significant_digits=4, number_format_notation="e",
                               number_to_string_func=custom_number_to_string)

        assert t1_hash[10] == t2_hash[50] == t1_hash[12] == t2_hash[63] != t1_hash[100000]

    def test_same_sets_in_lists_same_hash(self):
        t1 = ["a", {1, 3, 2}]
        t2 = [{2, 3, 1}, "a"]
        t1_hash = DeepHashPrep(t1)
        t2_hash = DeepHashPrep(t2)

        assert t1_hash[get_id(t1)] == t2_hash[get_id(t2)]

    def test_unknown_parameters(self):
        with pytest.raises(ValueError):
            DeepHashPrep(1, wrong_param=2)

    def test_bad_attribute_prep(self):
        class Bad:
            __slots__ = ['x', 'y']

            def __getattr__(self, key):
                raise AttributeError("Bad item")

            def __str__(self):
                return "Bad Object"

        t1 = Bad()

        result = DeepHashPrep(t1)
        expected_result = {t1: unprocessed, 'unprocessed': [t1]}
        assert expected_result == result

    class Burrito:
        bread = 'flour'

        def __init__(self):
            self.spicy = True

    class Taco:
        bread = 'flour'

        def __init__(self):
            self.spicy = True

    class ClassA:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    class ClassB:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    class ClassC(ClassB):
        pass

    obj_a = ClassA(1, 2)
    obj_b = ClassB(1, 2)
    obj_c = ClassC(1, 2)

    burrito = Burrito()
    taco = Taco()

    @pytest.mark.parametrize("t1, t2, ignore_type_in_groups, ignore_type_subclasses, is_qual", [
        (taco, burrito, [], False, False),
        (taco, burrito, [(Taco, Burrito)], False, True),
        ([taco], [burrito], [(Taco, Burrito)], False, True),
        ([obj_a], [obj_c], [(ClassA, ClassB)], False, False),
        ([obj_a], [obj_c], [(ClassA, ClassB)], True, True),
        ([obj_b], [obj_c], [(ClassB, )], True, True),
    ])
    def test_objects_with_same_content(self, t1, t2, ignore_type_in_groups, ignore_type_subclasses, is_qual):

        t1_result = DeepHashPrep(t1, ignore_type_in_groups=ignore_type_in_groups,
                                 ignore_type_subclasses=ignore_type_subclasses)
        t2_result = DeepHashPrep(t2, ignore_type_in_groups=ignore_type_in_groups,
                                 ignore_type_subclasses=ignore_type_subclasses)
        assert is_qual == (t1_result[t1] == t2_result[t2])

    def test_repetition_by_default_does_not_effect(self):
        list1 = [3, 4]
        list1_id = get_id(list1)
        a = [1, 2, list1]
        a_id = get_id(a)

        list2 = [4, 3, 3]
        list2_id = get_id(list2)
        b = [list2, 2, 1]
        b_id = get_id(b)

        hash_a = DeepHashPrep(a)
        hash_b = DeepHashPrep(b)

        assert hash_a[list1_id] == hash_b[list2_id]
        assert hash_a[a_id] == hash_b[b_id]

    def test_setting_repetition_off_unequal_hash(self):
        list1 = [3, 4]
        list1_id = get_id(list1)
        a = [1, 2, list1]
        a_id = get_id(a)

        list2 = [4, 3, 3]
        list2_id = get_id(list2)
        b = [list2, 2, 1]
        b_id = get_id(b)

        hash_a = DeepHashPrep(a, ignore_repetition=False)
        hash_b = DeepHashPrep(b, ignore_repetition=False)

        assert not hash_a[list1_id] == hash_b[list2_id]
        assert not hash_a[a_id] == hash_b[b_id]

        assert hash_a[list1_id].replace('3|1', '3|2') == hash_b[list2_id]

    def test_already_calculated_hash_wont_be_recalculated(self):
        hashes = (i for i in range(10))

        def hasher(obj):
            return str(next(hashes))

        obj = "a"
        expected_result = {obj: '0'}
        result = DeepHash(obj, hasher=hasher)
        assert expected_result == result

        # we simply feed the last result to DeepHash
        # So it can re-use the results.
        result2 = DeepHash(obj, hasher=hasher, hashes=result)
        # if hashes are not cached and re-used,
        # then the next time hasher runs, it returns
        # number 1 instead of 0.
        assert expected_result == result2

        result3 = DeepHash(obj, hasher=hasher)
        expected_result = {obj: '1'}
        assert expected_result == result3

    def test_skip_type(self):
        l1 = logging.getLogger("test")
        obj = {"log": l1, 2: 1337}
        result = DeepHashPrep(obj, exclude_types={logging.Logger})
        assert get_id(l1) not in result

    def test_skip_type2(self):
        l1 = logging.getLogger("test")
        result = DeepHashPrep(l1, exclude_types={logging.Logger})
        assert not result

    def test_prep_dic_with_loop(self):
        obj = {2: 1337}
        obj[1] = obj
        result = DeepHashPrep(obj)
        expected_result = {get_id(obj): 'dict:{int:2:int:1337}', 1: 'int:1', 2: 'int:2', 1337: 'int:1337'}
        assert expected_result == result

    def test_prep_iterable_with_loop(self):
        obj = [1]
        obj.append(obj)
        result = DeepHashPrep(obj)
        expected_result = {get_id(obj): 'list:int:1', 1: 'int:1'}
        assert expected_result == result

    def test_prep_iterable_with_excluded_type(self):
        l1 = logging.getLogger("test")
        obj = [1, l1]
        result = DeepHashPrep(obj, exclude_types={logging.Logger})
        assert get_id(l1) not in result

    def test_skip_str_type_in_dict_on_list(self):
        dic1 = {1: "a"}
        t1 = [dic1]
        dic2 = {}
        t2 = [dic2]
        t1_hash = DeepHashPrep(t1, exclude_types=[str])
        t2_hash = DeepHashPrep(t2, exclude_types=[str])
        assert 1 in t1_hash
        assert t1_hash[dic1] == t2_hash[dic2]

    def test_skip_path(self):
        dic1 = {1: "a"}
        t1 = [dic1, 2]
        dic2 = {}
        t2 = [dic2, 2]
        t1_hash = DeepHashPrep(t1, exclude_paths=['root[0]'])
        t2_hash = DeepHashPrep(t2, exclude_paths='root[0]')
        assert 1 not in t1_hash
        assert 2 in t1_hash
        assert t1_hash[2] == t2_hash[2]

    def test_skip_regex_path(self):
        dic1 = {1: "a"}
        t1 = [dic1, 2]
        exclude_re = re.compile(r'\[0\]')
        t1_hash = DeepHashPrep(t1, exclude_regex_paths=r'\[0\]')
        t2_hash = DeepHashPrep(t1, exclude_regex_paths=[exclude_re])
        assert 1 not in t1_hash
        assert 2 in t1_hash
        assert t1_hash[2] == t2_hash[2]

    def test_string_case(self):
        t1 = "Hello"

        t1_hash = DeepHashPrep(t1)
        assert t1_hash == {'Hello': 'str:Hello'}

        t1_hash = DeepHashPrep(t1, ignore_string_case=True)
        assert t1_hash == {'Hello': 'str:hello'}

    def test_hash_class(self):
        t1 = ClassC
        t1_hash = DeepHashPrep(t1)
        assert t1_hash['class_attr'] == 'str:class_attr'
        assert t1_hash[0] == 'int:0'
        # Note: we ignore private names in calculating hashes now. So you dont see __init__ here for example.
        assert t1_hash[t1] == r'objClassC:{str:class_attr:int:0}'


class TestDeepHashSHA:
    """DeepHash with SHA Tests."""

    def test_str_sha1(self):
        obj = "a"
        expected_result = {
            obj: '86f7e437faa5a7fce15d1ddcb9eaeaea377667b8'
        }
        result = DeepHash(obj, ignore_string_type_changes=True, hasher=DeepHash.sha1hex)
        assert expected_result == result

    def test_str_sha256(self):
        obj = "a"
        expected_result = {
            obj: 'ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb'
        }
        result = DeepHash(obj, ignore_string_type_changes=True, hasher=DeepHash.sha256hex)
        assert expected_result == result

    def test_prep_str_sha1_fail_if_mutable(self):
        """
        This test fails if DeepHash is getting a mutable copy of hashes
        which means each init of the DeepHash will have hashes from
        the previous init.
        """
        obj1 = "a"
        expected_result = {
            obj1: '86f7e437faa5a7fce15d1ddcb9eaeaea377667b8'
        }
        result = DeepHash(obj1, ignore_string_type_changes=True, hasher=DeepHash.sha1hex)
        assert expected_result == result
        obj2 = "b"
        result = DeepHash(obj2, ignore_string_type_changes=True, hasher=DeepHash.sha1hex)
        assert obj1 not in result

    def test_bytecode(self):
        obj = b"a"
        expected_result = {
            obj: '86f7e437faa5a7fce15d1ddcb9eaeaea377667b8'
        }
        result = DeepHash(obj, ignore_string_type_changes=True, hasher=DeepHash.sha1hex)
        assert expected_result == result

    def test_list1(self):
        string1 = "a"
        obj = [string1, 10, 20]
        expected_result = {
            string1: '86f7e437faa5a7fce15d1ddcb9eaeaea377667b8',
            get_id(obj): 'eac61cbd194e5e03c210a3dce67b9bfd6a7b7acb',
            10: DeepHash.sha1hex('int:10'),
            20: DeepHash.sha1hex('int:20'),
        }
        result = DeepHash(obj, ignore_string_type_changes=True, hasher=DeepHash.sha1hex)
        assert expected_result == result

    def test_dict1(self):
        string1 = "a"
        key1 = "key1"
        obj = {key1: string1, 1: 10, 2: 20}
        expected_result = {
            1: DeepHash.sha1hex('int:1'),
            10: DeepHash.sha1hex('int:10'),
            2: DeepHash.sha1hex('int:2'),
            20: DeepHash.sha1hex('int:20'),
            key1: '1073ab6cda4b991cd29f9e83a307f34004ae9327',
            string1: '86f7e437faa5a7fce15d1ddcb9eaeaea377667b8',
            get_id(obj): '11e23f096df81b1ccab0c309cdf8b4ba5a0a6895'
        }
        result = DeepHash(obj, ignore_string_type_changes=True, hasher=DeepHash.sha1hex)
        assert expected_result == result


class TestCleaningString:

    @pytest.mark.parametrize("text, ignore_string_type_changes, expected_result", [
        (b'hello', True, 'hello'),
        (b'hello', False, 'bytes:hello'),
        ('hello', True, 'hello'),
        ('hello', False, 'str:hello'),
    ])
    def test_clean_type(self, text, ignore_string_type_changes, expected_result):
        result = prepare_string_for_hashing(text, ignore_string_type_changes=ignore_string_type_changes)
        assert expected_result == result


class TestDeepHashMurmur3:
    """DeepHash with Murmur3 Hash Tests."""

    def test_prep_str_murmur3_64bit(self):
        obj = "a"
        expected_result = {
            obj: 424475663186367154
        }
        result = DeepHash(obj, ignore_string_type_changes=True, hasher=DeepHash.murmur3_64bit)
        assert expected_result == result

    def test_prep_str_murmur3_128bit(self):
        obj = "a"
        expected_result = {
            obj: 119173504597196970070553896747624927922
        }
        result = DeepHash(obj, ignore_string_type_changes=True, hasher=DeepHash.murmur3_128bit)
        assert expected_result == result
