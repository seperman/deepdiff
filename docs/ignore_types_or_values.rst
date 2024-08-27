:doc:`/index`

Ignore Types Or Values
======================

DeepDiff provides numerous functionalities for the user to be able to define what paths, item types etc. to be included or ignored during the diffing process.

As an example, you may have a type change in your objects:

Type change
    >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
    >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":"world\n\n\nEnd"}}
    >>> ddiff = DeepDiff(t1, t2)
    >>> pprint (ddiff, indent = 2)
    { 'type_changes': { "root[4]['b']": { 'new_type': <class 'str'>,
                                          'new_value': 'world\n\n\nEnd',
                                          'old_type': <class 'list'>,
                                          'old_value': [1, 2, 3]}}}

And if you don't care about the value of items that have changed type, you can set verbose level to 0
    >>> t1 = {1:1, 2:2, 3:3}
    >>> t2 = {1:1, 2:"2", 3:3}
    >>> pprint(DeepDiff(t1, t2, verbose_level=0), indent=2)
    { 'type_changes': { 'root[2]': { 'new_type': <class 'str'>,
                                     'old_type': <class 'int'>}}}


But what if you did not care about the integer becoming a string with the same value? What if you didn't want 2 -> "2" to be considered a type or value change? Throughout this page you will find different examples of functionalities that can help you achieve what you want.


.. _exclude_types_label:

Exclude Types
-------------

exclude_types: list, default = None
    List of object types to exclude from the report.

Exclude certain types from comparison:
    >>> l1 = logging.getLogger("test")
    >>> l2 = logging.getLogger("test2")
    >>> t1 = {"log": l1, 2: 1337}
    >>> t2 = {"log": l2, 2: 1337}
    >>> print(DeepDiff(t1, t2, exclude_types={logging.Logger}))
    {}

.. _ignore_string_type_changes_label:

Ignore String Type Changes
--------------------------

ignore_string_type_changes: Boolean, default = False
    Whether to ignore string type changes or not. For example b"Hello" vs. "Hello" are considered the same if ignore_string_type_changes is set to True.

    >>> DeepDiff(b'hello', 'hello', ignore_string_type_changes=True)
    {}
    >>> DeepDiff(b'hello', 'hello')
    {'type_changes': {'root': {'old_type': <class 'bytes'>, 'new_type': <class 'str'>, 'old_value': b'hello', 'new_value': 'hello'}}}

.. _ignore_numeric_type_changes_label:

Ignore Numeric Type Changes
---------------------------

ignore_numeric_type_changes: Boolean, default = False
    Whether to ignore numeric type changes or not. For example 10 vs. 10.0 are considered the same if ignore_numeric_type_changes is set to True.

Example
    >>> from decimal import Decimal
    >>> from deepdiff import DeepDiff
    >>> 
    >>> t1 = Decimal('10.01')
    >>> t2 = 10.01
    >>> 
    >>> DeepDiff(t1, t2)
    {'type_changes': {'root': {'old_type': <class 'decimal.Decimal'>, 'new_type': <class 'float'>, 'old_value': Decimal('10.01'), 'new_value': 10.01}}}
    >>> DeepDiff(t1, t2, ignore_numeric_type_changes=True)
    {}

Note that this parameter only works for comparing numbers with numbers. If you compare a number to a string value of the number, this parameter does not solver your problem:

Example:
    >>> t1 = Decimal('10.01')
    >>> t2 = "10.01"
    >>> 
    >>> DeepDiff(t1, t2, ignore_numeric_type_changes=True)
    {'type_changes': {'root': {'old_type': <class 'decimal.Decimal'>, 'new_type': <class 'str'>, 'old_value': Decimal('10.01'), 'new_value': '10.01'}}}

If you face repeated patterns of comparing numbers to string values of numbers, you will want to preprocess your input to convert the strings into numbers before feeding it into DeepDiff.


.. _ignore_type_in_groups_label:

Ignore Type In Groups
---------------------

ignore_type_in_groups: Tuple or List of Tuples, default = None
    Ignore type changes between members of groups of types. For example if you want to ignore type changes between float and decimals etc. Note that this is a more granular feature. While this feature is production ready for strings and numbers, it is still experimental with other custom lists of types, Hence it is recommended to use the shortcuts provided to you which are :ref:`ignore_string_type_changes_label` and :ref:`ignore_numeric_type_changes_label` unless you have a specific need beyond those 2 cases and you need do define your own ignore_type_in_groups.

    For example lets say you have specifically str and byte datatypes to be ignored for type changes. Then you have a couple of options:

    1. Set ignore_string_type_changes=True.
    2. Or set ignore_type_in_groups=[(str, bytes)]. Here you are saying if we detect one type to be str and the other one bytes, do not report them as type change. It is exactly as passing ignore_type_in_groups=[DeepDiff.strings] or ignore_type_in_groups=DeepDiff.strings .

    Now what if you want also typeA and typeB to be ignored when comparing against each other?

    1. ignore_type_in_groups=[DeepDiff.strings, (typeA, typeB)]
    2. or ignore_type_in_groups=[(str, bytes), (typeA, typeB)]


Note: The example below shows you have to use this feature. For enum types, however, you can just use :ref:`use_enum_value_label`

Example: Ignore Enum to string comparison
    >>> from deepdiff import DeepDiff
    >>> from enum import Enum
    >>> class MyEnum1(Enum):
    ...     book = "book"
    ...     cake = "cake"
    ...
    >>> DeepDiff("book", MyEnum1.book)
    {'type_changes': {'root': {'old_type': <class 'str'>, 'new_type': <enum 'MyEnum1'>, 'old_value': 'book', 'new_value': <MyEnum1.book: 'book'>}}}
    >>> DeepDiff("book", MyEnum1.book, ignore_type_in_groups=[(Enum, str)])
    {}


Example: Ignore Type Number - Dictionary that contains float and integer. Note that this is exactly the same as passing ignore_numeric_type_changes=True.
    >>> from deepdiff import DeepDiff
    >>> from pprint import pprint
    >>> t1 = {1: 1, 2: 2.22}
    >>> t2 = {1: 1.0, 2: 2.22}
    >>> ddiff = DeepDiff(t1, t2)
    >>> pprint(ddiff, indent=2)
    { 'type_changes': { 'root[1]': { 'new_type': <class 'float'>,
                                     'new_value': 1.0,
                                     'old_type': <class 'int'>,
                                     'old_value': 1}}}
    >>> ddiff = DeepDiff(t1, t2, ignore_type_in_groups=DeepDiff.numbers)
    >>> pprint(ddiff, indent=2)
    {}

Example: Ignore Type Number - List that contains float and integer. Note that this is exactly the same as passing ignore_numeric_type_changes=True.
    >>> from deepdiff import DeepDiff
    >>> from pprint import pprint
    >>> t1 = [1, 2, 3]
    >>> t2 = [1.0, 2.0, 3.0]
    >>> ddiff = DeepDiff(t1, t2)
    >>> pprint(ddiff, indent=2)
    { 'type_changes': { 'root[0]': { 'new_type': <class 'float'>,
                                     'new_value': 1.0,
                                     'old_type': <class 'int'>,
                                     'old_value': 1},
                        'root[1]': { 'new_type': <class 'float'>,
                                     'new_value': 2.0,
                                     'old_type': <class 'int'>,
                                     'old_value': 2},
                        'root[2]': { 'new_type': <class 'float'>,
                                     'new_value': 3.0,
                                     'old_type': <class 'int'>,
                                     'old_value': 3}}}
    >>> ddiff = DeepDiff(t1, t2, ignore_type_in_groups=DeepDiff.numbers)
    >>> pprint(ddiff, indent=2)
    {}

You can pass a list of tuples or list of lists if you have various type groups. When t1 and t2 both fall under one of these type groups, the type change will be ignored. DeepDiff already comes with 2 groups: DeepDiff.strings and DeepDiff.numbers . If you want to pass both:
    >>> ignore_type_in_groups = [DeepDiff.strings, DeepDiff.numbers]


ignore_type_in_groups example with custom objects:
    >>> class Burrito:
    ...     bread = 'flour'
    ...     def __init__(self):
    ...         self.spicy = True
    ...
    >>>
    >>> class Taco:
    ...     bread = 'flour'
    ...     def __init__(self):
    ...         self.spicy = True
    ...
    >>>
    >>> burrito = Burrito()
    >>> taco = Taco()
    >>>
    >>> burritos = [burrito]
    >>> tacos = [taco]
    >>>
    >>> DeepDiff(burritos, tacos, ignore_type_in_groups=[(Taco, Burrito)], ignore_order=True)
    {}

.. note::
    You can pass list of tuples of types to ignore_type_in_groups or you can put actual values in the tuples and ignore_type_in_groups will extract the type from them. The example below has used (1, 1.0) instead of (int, float),

Ignoring string to None comparison:
    >>> from deepdiff import DeepDiff
    >>> import datetime
    >>> 
    >>> t1 = [1, 2, 3, 'a', None]
    >>> t2 = [1.0, 2.0, 3.3, b'a', 'hello']
    >>> DeepDiff(t1, t2, ignore_type_in_groups=[(1, 1.0), (None, str, bytes)])
    {'values_changed': {'root[2]': {'new_value': 3.3, 'old_value': 3}}}
    >>> 

Ignoring datetime to string comparison
    >>> now = datetime.datetime(2020, 5, 5)
    >>> t1 = [1, 2, 3, 'a', now]
    >>> t2 = [1, 2, 3, 'a', 'now']
    >>> DeepDiff(t1, t2, ignore_type_in_groups=[(str, bytes, datetime.datetime)])
    {'values_changed': {'root[4]': {'new_value': 'now', 'old_value': datetime.datetime(2020, 5, 5, 0, 0)}}}


.. _ignore_type_subclasses_label:

Ignore Type Subclasses
----------------------

ignore_type_subclasses: Boolean, default = False
    Use ignore_type_subclasses=True so when ignoring type (class), the subclasses of that class are ignored too.

.. Note::
    ignore_type_subclasses was incorrectly doing the reverse of its job up until DeepDiff 6.7.1
    Please make sure to flip it in your use cases, when upgrading from older versions to 7.0.0 or above.

    >>> from deepdiff import DeepDiff
    >>> class ClassA:
    ...     def __init__(self, x, y):
    ...         self.x = x
    ...         self.y = y
    ...
    >>> class ClassB:
    ...     def __init__(self, x):
    ...         self.x = x
    ...
    >>> class ClassC(ClassB):
    ...     pass
    ...
    >>> obj_a = ClassA(1, 2)
    >>> obj_c = ClassC(3)
    >>>
    >>> DeepDiff(obj_a, obj_c, ignore_type_in_groups=[(ClassA, ClassB)], ignore_type_subclasses=True)
    {'type_changes': {'root': {'old_type': <class '__main__.ClassA'>, 'new_type': <class '__main__.ClassC'>, 'old_value': <__main__.ClassA object at 0x10076a2e8>, 'new_value': <__main__.ClassC object at 0x10082f630>}}}
    >>>
    >>> DeepDiff(obj_a, obj_c, ignore_type_in_groups=[(ClassA, ClassB)], ignore_type_subclasses=False)
    {'values_changed': {'root.x': {'new_value': 3, 'old_value': 1}}, 'attribute_removed': [root.y]}



.. _ignore_string_case_label:

Ignore String Case
------------------

ignore_string_case: Boolean, default = False
    Whether to be case-sensitive or not when comparing strings. By settings ignore_string_case=False, strings will be compared case-insensitively.

    >>> DeepDiff(t1='Hello', t2='heLLO')
    {'values_changed': {'root': {'new_value': 'heLLO', 'old_value': 'Hello'}}}
    >>> DeepDiff(t1='Hello', t2='heLLO', ignore_string_case=True)
    {}

Ignore Nan Inequality
---------------------

ignore_nan_inequality: Boolean, default = False
    Read more at :ref:`ignore_nan_inequality_label`
    Whether to ignore float('nan') inequality in Python.


.. _ignore_private_variables_label:

Ignore Private Variables
------------------------

ignore_private_variables: Boolean, default = True
    Whether to exclude the private variables in the calculations or not. It only affects variables that start with double underscores (__).


.. _exclude_obj_callback_label:

Exclude Obj Callback
--------------------

exclude_obj_callback: function, default = None
    A function that takes the object and its path and returns a Boolean. If True is returned, the object is excluded from the results, otherwise it is included.
    This is to give the user a higher level of control than one can achieve via exclude_paths, exclude_regex_paths or other means.

    >>> def exclude_obj_callback(obj, path):
    ...     return True if "skip" in path or isinstance(obj, int) else False
    ...
    >>> t1 = {"x": 10, "y": "b", "z": "c", "skip_1": 0}
    >>> t2 = {"x": 12, "y": "b", "z": "c", "skip_2": 0}
    >>> DeepDiff(t1, t2, exclude_obj_callback=exclude_obj_callback)
    {}


.. _exclude_obj_callback_strict_label:

Exclude Obj Callback Strict
---------------------------

exclude_obj_callback_strict: function, default = None
    A function that works the same way as exclude_obj_callback, but excludes elements from the result only if the function returns True for both elements

    >>> def exclude_obj_callback_strict(obj, path):
    ...         return True if isinstance(obj, int) and obj > 10 else False
    ...
    >>> t1 = {"x": 10, "y": "b", "z": "c"}
    >>> t2 = {"x": 12, "y": "b", "z": "c"}
    >>> DeepDiff(t1, t2, exclude_obj_callback=exclude_obj_callback_strict)
    {}
    >>> DeepDiff(t1, t2, exclude_obj_callback_strict=exclude_obj_callback_strict)
    {'values_changed': {"root['x']": {'new_value': 12, 'old_value': 10}}}


.. _include_obj_callback_label:

Include Obj Callback
--------------------

include_obj_callback: function, default = None
    A function that takes the object and its path and returns a Boolean. If True is returned, the object is included in the results, otherwise it is excluded.
    This is to give the user a higher level of control than one can achieve via include_paths.

    >>> def include_obj_callback(obj, path):
    ...     return True if "include" in path or isinstance(obj, int) else False
    ...
    >>> t1 = {"x": 10, "y": "b", "z": "c", "include_me": "a"}
    >>> t2 = {"x": 10, "y": "b", "z": "c", "include_me": "b"}
    >>> DeepDiff(t1, t2, include_obj_callback=include_obj_callback)
    {'values_changed': {"root['include_me']": {'new_value': "b", 'old_value': "a"}}}


.. _include_obj_callback_strict_label:

Include Obj Callback Strict
---------------------------

include_obj_callback_strict: function, default = None
    A function that works the same way as include_obj_callback, but includes elements in the result only if the function returns True for both elements.

    >>> def include_obj_callback_strict(obj, path):
    ...         return True if isinstance(obj, int) and obj > 10 else False
    ...
    >>> t1 = {"x": 10, "y": "b", "z": "c"}
    >>> t1 = {"x": 12, "y": "b", "z": "c"}
    >>> DeepDiff(t1, t2, include_obj_callback=include_obj_callback_strict)
    {'values_changed': {"root['x']": {'new_value': 12, 'old_value': 10}}}
    >>> DeepDiff(t1, t2, include_obj_callback_strict=include_obj_callback_strict)
    {}


.. _truncate_datetime_label:

Truncate Datetime
-----------------

truncate_datetime: string, default = None
    truncate_datetime can take value one of 'second', 'minute', 'hour', 'day' and truncate with this value datetime objects before hashing it

    >>> import datetime
    >>> from deepdiff import DeepDiff
    >>> d1 = {'a': datetime.datetime(2020, 5, 17, 22, 15, 34, 913070)}
    >>> d2 = {'a': datetime.datetime(2020, 5, 17, 22, 15, 39, 296583)}
    >>> DeepDiff(d1, d2, truncate_datetime='minute')
    {}


.. _use_enum_value_label:

Use Enum Value
--------------

use_enum_value: Boolean, default=False
    Makes it so when diffing enum, we use the enum's value. It makes it so comparing an enum to a string or any other value is not reported as a type change.

    >>> from enum import Enum
    >>> from deepdiff import DeepDiff

    >>>
    >>> class MyEnum2(str, Enum):
    ...     book = "book"
    ...     cake = "cake"
    ...
    >>> DeepDiff("book", MyEnum2.book)
    {'type_changes': {'root': {'old_type': <class 'str'>, 'new_type': <enum 'MyEnum2'>, 'old_value': 'book', 'new_value': <MyEnum2.book: 'book'>}}}
    >>> DeepDiff("book", MyEnum2.book, use_enum_value=True)
    {}


Back to :doc:`/index`
