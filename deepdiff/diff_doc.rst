**DeepDiff**

Deep Difference of dictionaries, iterables, strings and almost any other object.
It will recursively look for all the changes.

**Parameters**

t1 : A dictionary, list, string or any python object that has __dict__ or __slots__
    This is the first item to be compared to the second item

t2 : dictionary, list, string or almost any python object that has __dict__ or __slots__
    The second item is to be compared to the first one

ignore_order : Boolean, default=False
    :ref:`ignore_order_label` ignores order of elements when comparing iterables (lists)
    Normally ignore_order does not report duplicates and repetition changes.
    In order to report repetitions, set report_repetition=True in addition to ignore_order=True

report_repetition : Boolean, default=False
    :ref:`report_repetition_label` reports repetitions when set True
    It only works when ignore_order is set to True too.

significant_digits : int >= 0, default=None
    :ref:`significant_digits_label` defines the number of digits AFTER the decimal point to be used in the comparison. However you can override that by setting the number_format_notation="e" which will make it mean the digits in scientific notation.

number_format_notation : string, default="f"
    :ref:`number_format_notation_label` is what defines the meaning of significant digits. The default value of "f" means the digits AFTER the decimal point. "f" stands for fixed point. The other option is "e" which stands for exponent notation or scientific notation.

number_to_string_func : function, default=None
    :ref:`number_to_string_func_label` is an advanced feature to give the user the full control into overriding how numbers are converted to strings for comparison. The default function is defined in https://github.com/seperman/deepdiff/blob/master/deepdiff/helper.py and is called number_to_string. You can define your own function to do that.

verbose_level: int >= 0, default = 1
    Higher verbose level shows you more details.
    For example verbose level 1 shows what dictionary item are added or removed.
    And verbose level 2 shows the value of the items that are added or removed too.
    Note that the verbose_level is ignore for the delta view.

exclude_paths: list, default = None
    List of paths to exclude from the report. If only one item, you can path it as a string.

exclude_regex_paths: list, default = None
    List of string regex paths or compiled regex paths objects to exclude from the report. If only one item, you can pass it as a string or regex compiled object.


hasher: default = DeepHash.murmur3_128bit
    Hash function to be used. If you don't want Murmur3, you can use Python's built-in hash function
    by passing hasher=hash. This is for advanced usage and normally you don't need to modify it.

view: string, default = text
    :ref:`view_label`
    Views are different "formats" of results. Each view comes with its own features.
    The choices are text (the default) and tree.
    The text view is the original format of the results.
    The tree view allows you to traverse through the tree of results. So you can traverse through the tree and see what items were compared to what.

exclude_types: list, default = None
    :ref:`exclude_types_label`
    List of object types to exclude from the report.

exclude_obj_callback: function, default = None
    :ref:`exclude_obj_callback_label`
    A function that takes the object and its path and returns a Boolean. If True is returned, the object is excluded from the results, otherwise it is included.
    This is to give the user a higher level of control than one can achieve via exclude_paths, exclude_regex_paths or other means.

ignore_string_type_changes: Boolean, default = False
    :ref:`ignore_string_type_changes_label`
    Whether to ignore string type changes or not. For example b"Hello" vs. "Hello" are considered the same if ignore_string_type_changes is set to True.

ignore_numeric_type_changes: Boolean, default = False
    :ref:`ignore_numeric_type_changes_label`
    Whether to ignore numeric type changes or not. For example 10 vs. 10.0 are considered the same if ignore_numeric_type_changes is set to True.

ignore_type_in_groups: Tuple or List of Tuples, default = None
    :ref:`ignore_type_in_groups_label`
    ignores types when t1 and t2 are both within the same type group.

ignore_type_subclasses: Boolean, default = False
    :ref:`ignore_type_subclasses_label`
    ignore type (class) changes when dealing with the subclasses of classes that were marked to be ignored.

ignore_string_case: Boolean, default = False
    :ref:`ignore_string_case_label`
    Whether to be case-sensitive or not when comparing strings. By settings ignore_string_case=False, strings will be compared case-insensitively.

ignore_nan_inequality: Boolean, default = False
    :ref:`ignore_nan_inequality_label`
    Whether to ignore float('nan') inequality in Python.

ignore_private_variables: Boolean, default = True
    :ref:`ignore_private_variables_label`
    Whether to exclude the private variables in the calculations or not. It only affects variables that start with double underscores (__).

max_passes: Integer, default = 10000000
    :ref:`max_passes_label` defined the maximum number of passes to run on objects to pin point what exactly is different. This is only used when ignore_order=True

log_frequency_in_sec: Integer, default = 0
    How often to log the progress. The default of 0 means logging progress is disabled.
    If you set it to 20, it will log every 20 seconds. This is useful only when running DeepDiff
    on massive objects that will take a while to run. If you are only dealing with small objects, keep it at 0 to disable progress logging.

progress_logger: log function, default = logger.warning
    What logging function to use specifically for progress reporting. This function is only used when progress logging is enabled
    by setting log_frequency_in_sec to anything above zero. The function that is passed needs to be thread safe.
    The reason that the default is logger.warning and not logger.info is that the logging is done via a separate thread and
    somehow the info logs get muted by default.


**Returns**

    A DeepDiff object that has already calculated the difference of the 2 items. The format of the object is chosen by the view parameter.

**Supported data types**

int, string, unicode, dictionary, list, tuple, set, frozenset, OrderedDict, NamedTuple, Numpy, custom objects and more!



Importing
    >>> from deepdiff import DeepDiff
    >>> from pprint import pprint

Same object returns empty
    >>> t1 = {1:1, 2:2, 3:3}
    >>> t2 = t1
    >>> print(DeepDiff(t1, t2))
    {}

Type of an item has changed
    >>> t1 = {1:1, 2:2, 3:3}
    >>> t2 = {1:1, 2:"2", 3:3}
    >>> pprint(DeepDiff(t1, t2), indent=2)
    { 'type_changes': { 'root[2]': { 'new_type': <class 'str'>,
                                     'new_value': '2',
                                     'old_type': <class 'int'>,
                                     'old_value': 2}}}

Value of an item has changed
    >>> t1 = {1:1, 2:2, 3:3}
    >>> t2 = {1:1, 2:4, 3:3}
    >>> pprint(DeepDiff(t1, t2, verbose_level=0), indent=2)
    {'values_changed': {'root[2]': {'new_value': 4, 'old_value': 2}}}

Item added and/or removed
    >>> t1 = {1:1, 3:3, 4:4}
    >>> t2 = {1:1, 3:3, 5:5, 6:6}
    >>> ddiff = DeepDiff(t1, t2)
    >>> pprint (ddiff)
    {'dictionary_item_added': [root[5], root[6]],
     'dictionary_item_removed': [root[4]]}

Set verbose level to 2 in order to see the added or removed items with their values
    >>> t1 = {1:1, 3:3, 4:4}
    >>> t2 = {1:1, 3:3, 5:5, 6:6}
    >>> ddiff = DeepDiff(t1, t2, verbose_level=2)
    >>> pprint(ddiff, indent=2)
    { 'dictionary_item_added': {'root[5]': 5, 'root[6]': 6},
      'dictionary_item_removed': {'root[4]': 4}}

String difference
    >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":"world"}}
    >>> t2 = {1:1, 2:4, 3:3, 4:{"a":"hello", "b":"world!"}}
    >>> ddiff = DeepDiff(t1, t2)
    >>> pprint (ddiff, indent = 2)
    { 'values_changed': { 'root[2]': {'new_value': 4, 'old_value': 2},
                          "root[4]['b']": { 'new_value': 'world!',
                                            'old_value': 'world'}}}


String difference 2
    >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":"world!\nGoodbye!\n1\n2\nEnd"}}
    >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":"world\n1\n2\nEnd"}}
    >>> ddiff = DeepDiff(t1, t2)
    >>> pprint (ddiff, indent = 2)
    { 'values_changed': { "root[4]['b']": { 'diff': '--- \n'
                                                    '+++ \n'
                                                    '@@ -1,5 +1,4 @@\n'
                                                    '-world!\n'
                                                    '-Goodbye!\n'
                                                    '+world\n'
                                                    ' 1\n'
                                                    ' 2\n'
                                                    ' End',
                                            'new_value': 'world\n1\n2\nEnd',
                                            'old_value': 'world!\n'
                                                         'Goodbye!\n'
                                                         '1\n'
                                                         '2\n'
                                                         'End'}}}

    >>>
    >>> print (ddiff['values_changed']["root[4]['b']"]["diff"])
    --- 
    +++ 
    @@ -1,5 +1,4 @@
    -world!
    -Goodbye!
    +world
     1
     2
     End

List difference
    >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3, 4]}}
    >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2]}}
    >>> ddiff = DeepDiff(t1, t2)
    >>> pprint (ddiff, indent = 2)
    {'iterable_item_removed': {"root[4]['b'][2]": 3, "root[4]['b'][3]": 4}}

List that contains dictionary:
    >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, {1:1, 2:2}]}}
    >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, {1:3}]}}
    >>> ddiff = DeepDiff(t1, t2)
    >>> pprint (ddiff, indent = 2)
    { 'dictionary_item_removed': [root[4]['b'][2][2]],
      'values_changed': {"root[4]['b'][2][1]": {'new_value': 3, 'old_value': 1}}}

Sets:
    >>> t1 = {1, 2, 8}
    >>> t2 = {1, 2, 3, 5}
    >>> ddiff = DeepDiff(t1, t2)
    >>> pprint(ddiff)
    {'set_item_added': [root[3], root[5]], 'set_item_removed': [root[8]]}

Named Tuples:
    >>> from collections import namedtuple
    >>> Point = namedtuple('Point', ['x', 'y'])
    >>> t1 = Point(x=11, y=22)
    >>> t2 = Point(x=11, y=23)
    >>> pprint (DeepDiff(t1, t2))
    {'values_changed': {'root.y': {'new_value': 23, 'old_value': 22}}}

Custom objects:
    >>> class ClassA(object):
    ...     a = 1
    ...     def __init__(self, b):
    ...         self.b = b
    ...
    >>> t1 = ClassA(1)
    >>> t2 = ClassA(2)
    >>>
    >>> pprint(DeepDiff(t1, t2))
    {'values_changed': {'root.b': {'new_value': 2, 'old_value': 1}}}

Object attribute added:
    >>> t2.c = "new attribute"
    >>> pprint(DeepDiff(t1, t2))
    {'attribute_added': [root.c],
     'values_changed': {'root.b': {'new_value': 2, 'old_value': 1}}}


.. note::
    All the examples for the text view work for the tree view too.
    You just need to set view='tree' to get it in tree form.


**Ignore Type Changes**






ignore_numeric_type_changes Default: False
    Ignore Type Number - Dictionary that contains float and integer
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

Ignore Type Number - List that contains float and integer
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





**Exclude paths**

Exclude part of your object tree from comparison
use `exclude_paths` and pass a set or list of paths to exclude, if only one item is being passed, then just put it there as a string. No need to pass it as a list then.
    >>> t1 = {"for life": "vegan", "ingredients": ["no meat", "no eggs", "no dairy"]}
    >>> t2 = {"for life": "vegan", "ingredients": ["veggies", "tofu", "soy sauce"]}
    >>> print (DeepDiff(t1, t2, exclude_paths="root['ingredients']"))  # one item pass it as a string
    {}
    >>> print (DeepDiff(t1, t2, exclude_paths=["root['ingredients']", "root['ingredients2']"]))  # multiple items pass as a list or a set.
    {}

You can also exclude using regular expressions by using `exclude_regex_paths` and pass a set or list of path regexes to exclude. The items in the list could be raw regex strings or compiled regex objects.
    >>> import re
    >>> t1 = [{'a': 1, 'b': 2}, {'c': 4, 'b': 5}]
    >>> t2 = [{'a': 1, 'b': 3}, {'c': 4, 'b': 5}]
    >>> print(DeepDiff(t1, t2, exclude_regex_paths=r"root\[\d+\]\['b'\]"))
    {}
    >>> exclude_path = re.compile(r"root\[\d+\]\['b'\]")
    >>> print(DeepDiff(t1, t2, exclude_regex_paths=[exclude_path]))
    {}

example 2:
    >>> t1 = {'a': [1, 2, [3, {'foo1': 'bar'}]]}
    >>> t2 = {'a': [1, 2, [3, {'foo2': 'bar'}]]}
    >>> DeepDiff(t1, t2, exclude_regex_paths="\['foo.'\]")  # since it is one item in exclude_regex_paths, you don't have to put it in a list or a set.
    {}

Tip: DeepDiff is using re.search on the path. So if you want to force it to match from the beginning of the path, add `^` to the beginning of regex.



.. note::
    All the examples for the text view work for the tree view too. You just need to set view='tree' to get it in tree form.

**Serialization**

In order to convert the DeepDiff object into a normal Python dictionary, use the to_dict() method.
Note that you can override the view that was originally used to generate the diff here.

Example:
    >>> t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3]}}
    >>> t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world\n\n\nEnd"}}
    >>> ddiff = DeepDiff(t1, t2, view='tree')
    >>> ddiff.to_dict(view_override='text')
    {'type_changes': {"root[4]['b']": {'old_type': <class 'list'>, 'new_type': <class 'str'>, 'old_value': [1, 2, 3], 'new_value': 'world\n\n\nEnd'}}}


In order to do safe json serialization, use the to_json() method.

Example:
    >>> t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3]}}
    >>> t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world\n\n\nEnd"}}
    >>> ddiff = DeepDiff(t1, t2, view='tree')
    >>> ddiff.to_json()
    '{"type_changes": {"root[4][\'b\']": {"old_type": "list", "new_type": "str", "old_value": [1, 2, 3], "new_value": "world\\n\\n\\nEnd"}}}'

.. seealso::
    Take a look at to_json() documentation in this page for more details.

If you want the original DeepDiff object to be serialized with all the bells and whistles, you can use the to_json_pickle() and from_json_pickle() in order to serialize and deserialize its results into json. Note that json_pickle is unsafe and json pickle dumps from untrusted sources should never be loaded.

Serialize and then deserialize back to deepdiff
    >>> t1 = {1: 1, 2: 2, 3: 3}
    >>> t2 = {1: 1, 2: "2", 3: 3}
    >>> ddiff = DeepDiff(t1, t2)
    >>> jsoned = ddiff.to_json_pickle()
    >>> jsoned
    '{"type_changes": {"root[2]": {"new_type": {"py/type": "builtins.str"}, "new_value": "2", "old_type": {"py/type": "builtins.int"}, "old_value": 2}}}'
    >>> ddiff_new = DeepDiff.from_json_pickle(jsoned)
    >>> ddiff == ddiff_new
    True
