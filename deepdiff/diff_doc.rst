**DeepDiff**

Deep Difference of dictionaries, iterables, strings and almost any other object.
It will recursively look for all the changes.

DeepDiff 3.0 added the concept of views.
There is a default "text" view and a "tree" view.

**Parameters**

t1 : A dictionary, list, string or any python object that has __dict__ or __slots__
    This is the first item to be compared to the second item

t2 : dictionary, list, string or almost any python object that has __dict__ or __slots__
    The second item is to be compared to the first one

ignore_order : Boolean, defalt=False ignores orders for iterables.
    Note that if you have iterables contatining any unhashable, ignoring order can be expensive.
    Normally ignore_order does not report duplicates and repetition changes.
    In order to report repetitions, set report_repetition=True in addition to ignore_order=True

report_repetition : Boolean, default=False reports repetitions when set True
    ONLY when ignore_order is set True too. This works for iterables.
    This feature currently is experimental and is not production ready.

significant_digits : int >= 0, default=None.
    If it is a non negative integer, it compares only that many digits AFTER
    the decimal point.

    This only affects floats, decimal.Decimal and complex.

    Internally it uses "{:.Xf}".format(Your Number) to compare numbers where X=significant_digits

    Note that "{:.3f}".format(1.1135) = 1.113, but "{:.3f}".format(1.11351) = 1.114

    For Decimals, Python's format rounds 2.5 to 2 and 3.5 to 4 (to the closest even number)

verbose_level : int >= 0, default = 1.
    Higher verbose level shows you more details.
    For example verbose level 1 shows what dictionary item are added or removed.
    And verbose level 2 shows the value of the items that are added or removed too.

exclude_paths: list, default = None
    List of paths to exclude from the report. If only one item, you can path it as a string.

exclude_regex_paths: list, default = None
    List of string regex paths or compiled regex paths objects to exclude from the report. If only one item, you can pass it as a string or regex compiled object.


hasher: default = DeepHash.murmur3_128bit
    Hash function to be used. If you don't want Murmur3, you can use Python's built-in hash function
    by passing hasher=hash. This is for advanced usage and normally you don't need to modify it.

view: string, default = text
    Starting the version 3 you can choosethe view into the deepdiff results.
    The default is the text view which has been the only view up until now.
    The new view is called the tree view which allows you to traverse through
    the tree of changed items.

exclude_types: list, default = None
    List of object types to exclude from the report.

ignore_string_type_changes: Boolean, default = False
    Whether to ignore string type changes or not. For example b"Hello" vs. "Hello" are considered the same if ignore_string_type_changes is set to True.

ignore_numeric_type_changes: Boolean, default = False
    Whether to ignore numeric type changes or not. For example 10 vs. 10.0 are considered the same if ignore_numeric_type_changes is set to True.

ignore_type_in_groups: Tuple or List of Tuples, default = None
    ignores types when t1 and t2 are both within the same type group.

**Returns**

    A DeepDiff object that has already calculated the difference of the 2 items.

**Supported data types**

int, string, unicode, dictionary, list, tuple, set, frozenset, OrderedDict, NamedTuple and custom objects!

**Text View**

Text view is the original and currently the default view of DeepDiff.

It is called text view because the results contain texts that represent the path to the data:

Example of using the text view.
    >>> from deepdiff import DeepDiff
    >>> t1 = {1:1, 3:3, 4:4}
    >>> t2 = {1:1, 3:3, 5:5, 6:6}
    >>> ddiff = DeepDiff(t1, t2)
    >>> print(ddiff)
    {'dictionary_item_added': [root[5], root[6]], 'dictionary_item_removed': [root[4]]}

So for example ddiff['dictionary_item_added'] is a set of strings thus this is called the text view.

.. seealso::
    The following examples are using the *default text view.*
    The Tree View is introduced in DeepDiff v3 and provides
    traversing capabilitie through your diffed data and more!
    Read more about the Tree View at the bottom of this page.

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

List difference 2:
    >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
    >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 3, 2, 3]}}
    >>> ddiff = DeepDiff(t1, t2)
    >>> pprint (ddiff, indent = 2)
    { 'iterable_item_added': {"root[4]['b'][3]": 3},
      'values_changed': { "root[4]['b'][1]": {'new_value': 3, 'old_value': 2},
                          "root[4]['b'][2]": {'new_value': 2, 'old_value': 3}}}

List difference ignoring order or duplicates: (with the same dictionaries as above)
    >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
    >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 3, 2, 3]}}
    >>> ddiff = DeepDiff(t1, t2, ignore_order=True)
    >>> print (ddiff)
    {}

List difference ignoring order but reporting repetitions:
    >>> from deepdiff import DeepDiff
    >>> from pprint import pprint
    >>> t1 = [1, 3, 1, 4]
    >>> t2 = [4, 4, 1]
    >>> ddiff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True)
    >>> pprint(ddiff, indent=2)
    { 'iterable_item_removed': {'root[1]': 3},
      'repetition_change': { 'root[0]': { 'new_indexes': [2],
                                          'new_repeat': 1,
                                          'old_indexes': [0, 2],
                                          'old_repeat': 2,
                                          'value': 1},
                             'root[3]': { 'new_indexes': [0, 1],
                                          'new_repeat': 2,
                                          'old_indexes': [3],
                                          'old_repeat': 1,
                                          'value': 4}}}

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

Approximate decimals comparison (Significant digits after the point):
    >>> t1 = Decimal('1.52')
    >>> t2 = Decimal('1.57')
    >>> DeepDiff(t1, t2, significant_digits=0)
    {}
    >>> DeepDiff(t1, t2, significant_digits=1)
    {'values_changed': {'root': {'new_value': Decimal('1.57'), 'old_value': Decimal('1.52')}}}

Approximate float comparison (Significant digits after the point):
    >>> t1 = [ 1.1129, 1.3359 ]
    >>> t2 = [ 1.113, 1.3362 ]
    >>> pprint(DeepDiff(t1, t2, significant_digits=3))
    {}
    >>> pprint(DeepDiff(t1, t2))
    {'values_changed': {'root[0]': {'new_value': 1.113, 'old_value': 1.1129},
                        'root[1]': {'new_value': 1.3362, 'old_value': 1.3359}}}
    >>> pprint(DeepDiff(1.23*10**20, 1.24*10**20, significant_digits=1))
    {'values_changed': {'root': {'new_value': 1.24e+20, 'old_value': 1.23e+20}}}


.. note::
    All the examples for the text view work for the tree view too.
    You just need to set view='tree' to get it in tree form.


**Ignore Type Changes**

Type change
    >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
    >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":"world\n\n\nEnd"}}
    >>> ddiff = DeepDiff(t1, t2)
    >>> pprint (ddiff, indent = 2)
    { 'type_changes': { "root[4]['b']": { 'new_type': <class 'str'>,
                                          'new_value': 'world\n\n\nEnd',
                                          'old_type': <class 'list'>,
                                          'old_value': [1, 2, 3]}}}

And if you don't care about the value of items that have changed type, please set verbose level to 0
    >>> t1 = {1:1, 2:2, 3:3}
    >>> t2 = {1:1, 2:"2", 3:3}
    >>> pprint(DeepDiff(t1, t2, verbose_level=0), indent=2)
    { 'type_changes': { 'root[2]': { 'new_type': <class 'str'>,
                                     'old_type': <class 'int'>}}}


Exclude types

Exclude certain types from comparison:
    >>> l1 = logging.getLogger("test")
    >>> l2 = logging.getLogger("test2")
    >>> t1 = {"log": l1, 2: 1337}
    >>> t2 = {"log": l2, 2: 1337}
    >>> print(DeepDiff(t1, t2, exclude_types={logging.Logger}))
    {}

ignore_type_in_groups

Ignore type changes between members of groups of types. For example if you want to ignore type changes between float and decimals etc. Note that this is a more granular feature. Most of the times the shortcuts provided to you are enough.
The shortcuts are ignore_string_type_changes which by default is False and ignore_numeric_type_changes which is by default False. You can read more about those shortcuts in this page. ignore_type_in_groups gives you more control compared to the shortcuts.

For example lets say you have specifically str and byte datatypes to be ignored for type changes. Then you have a couple of options:

1. Set ignore_string_type_changes=True.
2. Or set ignore_type_in_groups=[(str, bytes)]. Here you are saying if we detect one type to be str and the other one bytes, do not report them as type change. It is exactly as passing ignore_type_in_groups=[DeepDiff.strings] or ignore_type_in_groups=DeepDiff.strings .

Now what if you want also typeA and typeB to be ignored when comparing agains each other?

1. ignore_type_in_groups=[DeepDiff.strings, (typeA, typeB)]
2. or ignore_type_in_groups=[(str, bytes), (typeA, typeB)]

ignore_string_type_changes
Default: False
    >>> DeepDiff(b'hello', 'hello', ignore_string_type_changes=True)
    {}
    >>> DeepDiff(b'hello', 'hello')
    {'type_changes': {'root': {'old_type': <class 'bytes'>, 'new_type': <class 'str'>, 'old_value': b'hello', 'new_value': 'hello'}}}

ignore_numeric_type_changes
Default: False

Ignore Type Number - Dictionary that contains float and integer:
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

Ignore Type Number - List that contains float and integer:
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


**Tree View**

Starting the version 3 You can chooe the view into the deepdiff results.
The tree view provides you with tree objects that you can traverse through to find
the parents of the objects that are diffed and the actual objects that are being diffed.
This view is very useful when dealing with nested objects.
Note that tree view always returns results in the form of Python sets.

You can traverse through the tree elements!

.. note::
    The Tree view is just a different representation of the diffed data.
    Behind the scene, DeepDiff creates the tree view first and then converts it to textual
    representation for the text view.

.. code:: text

    +---------------------------------------------------------------+
    |                                                               |
    |    parent(t1)              parent node            parent(t2)  |
    |      +                          ^                     +       |
    +------|--------------------------|---------------------|-------+
           |                      |   | up                  |
           | Child                |   |                     | ChildRelationship
           | Relationship         |   |                     |
           |                 down |   |                     |
    +------|----------------------|-------------------------|-------+
    |      v                      v                         v       |
    |    child(t1)              child node               child(t2)  |
    |                                                               |
    +---------------------------------------------------------------+


:up: Move up to the parent node
:down: Move down to the child node
:path(): Get the path to the current node
:t1: The first item in the current node that is being diffed
:t2: The second item in the current node that is being diffed
:additional: Additional information about the node i.e. repetition
:repetition: Shortcut to get the repetition report


The tree view allows you to have more than mere textual representaion of the diffed objects.
It gives you the actual objects (t1, t2) throughout the tree of parents and children.

**Examples Tree View**

.. note::
    The Tree View is introduced in DeepDiff 3.
    Set view='tree' in order to use this view.

Value of an item has changed (Tree View)
    >>> from deepdiff import DeepDiff
    >>> from pprint import pprint
    >>> t1 = {1:1, 2:2, 3:3}
    >>> t2 = {1:1, 2:4, 3:3}
    >>> ddiff_verbose0 = DeepDiff(t1, t2, verbose_level=0, view='tree')
    >>> ddiff_verbose0
    {'values_changed': [<root[2]>]}
    >>>
    >>> ddiff_verbose1 = DeepDiff(t1, t2, verbose_level=1, view='tree')
    >>> ddiff_verbose1
    {'values_changed': [<root[2] t1:2, t2:4>]}
    >>> set_of_values_changed = ddiff_verbose1['values_changed']
    >>> # since set_of_values_changed includes only one item in a set
    >>> # in order to get that one item we can:
    >>> (changed,) = set_of_values_changed
    >>> changed  # Another way to get this is to do: changed=list(set_of_values_changed)[0]
    <root[2] t1:2, t2:4>
    >>> changed.t1
    2
    >>> changed.t2
    4
    >>> # You can traverse through the tree, get to the parents!
    >>> changed.up
    <root t1:{1: 1, 2: 2,...}, t2:{1: 1, 2: 4,...}>

List difference (Tree View)
    >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3, 4]}}
    >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2]}}
    >>> ddiff = DeepDiff(t1, t2, view='tree')
    >>> ddiff
    {'iterable_item_removed': [<root[4]['b'][2] t1:3, t2:not present>, <root[4]['b'][3] t1:4, t2:not present>]}
    >>> # Note that the iterable_item_removed is a set. In this case it has 2 items in it.
    >>> # One way to get one item from the set is to convert it to a list
    >>> # And then get the first item of the list:
    >>> removed = list(ddiff['iterable_item_removed'])[0]
    >>> removed
    <root[4]['b'][2] t1:3, t2:not present>
    >>>
    >>> parent = removed.up
    >>> parent
    <root[4]['b'] t1:[1, 2, 3, 4], t2:[1, 2]>
    >>> parent.path()
    "root[4]['b']"
    >>> parent.t1
    [1, 2, 3, 4]
    >>> parent.t2
    [1, 2]
    >>> parent.up
    <root[4] t1:{'a': 'hello...}, t2:{'a': 'hello...}>
    >>> parent.up.up
    <root t1:{1: 1, 2: 2,...}, t2:{1: 1, 2: 2,...}>
    >>> parent.up.up.t1
    {1: 1, 2: 2, 3: 3, 4: {'a': 'hello', 'b': [1, 2, 3, 4]}}
    >>> parent.up.up.t1 == t1  # It is holding the original t1 that we passed to DeepDiff
    True

List difference 2  (Tree View)
    >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
    >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 3, 2, 3]}}
    >>> ddiff = DeepDiff(t1, t2, view='tree')
    >>> pprint(ddiff, indent = 2)
    { 'iterable_item_added': [<root[4]['b'][3] t1:not present, t2:3>],
      'values_changed': [<root[4]['b'][1] t1:2, t2:3>, <root[4]['b'][2] t1:3, t2:2>]}
    >>>
    >>> # Note that iterable_item_added is a set with one item.
    >>> # So in order to get that one item from it, we can do:
    >>>
    >>> (added,) = ddiff['iterable_item_added']
    >>> added
    <root[4]['b'][3] t1:not present, t2:3>
    >>> added.up.up
    <root[4] t1:{'a': 'hello...}, t2:{'a': 'hello...}>
    >>> added.up.up.path()
    'root[4]'
    >>> added.up.up.down
    <root[4]['b'] t1:[1, 2, 3], t2:[1, 3, 2, 3]>
    >>>
    >>> # going up twice and then down twice gives you the same node in the tree:
    >>> added.up.up.down.down == added
    True

List difference ignoring order but reporting repetitions (Tree View)
    >>> t1 = [1, 3, 1, 4]
    >>> t2 = [4, 4, 1]
    >>> ddiff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True, view='tree')
    >>> pprint(ddiff, indent=2)
    { 'iterable_item_removed': [<root[1] t1:3, t2:not present>],
      'repetition_change': [<root[3] {'repetition': {'old_repeat': 1,...}>, <root[0] {'repetition': {'old_repeat': 2,...}>]}
    >>>
    >>> # repetition_change is a set with 2 items.
    >>> # in order to get those 2 items, we can do the following.
    >>> # or we can convert the set to list and get the list items.
    >>> # or we can iterate through the set items
    >>>
    >>> (repeat1, repeat2) = ddiff['repetition_change']
    >>> repeat1  # the default verbosity is set to 1.
    <root[3] {'repetition': {'old_repeat': 1,...}>
    >>> # The actual data regarding the repetitions can be found in the repetition attribute:
    >>> repeat1.repetition
    {'old_repeat': 1, 'new_repeat': 2, 'old_indexes': [3], 'new_indexes': [0, 1]}
    >>>
    >>> # If you change the verbosity, you will see less:
    >>> ddiff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True, view='tree', verbose_level=0)
    >>> ddiff
    {'repetition_change': [<root[3]>, <root[0]>], 'iterable_item_removed': [<root[1]>]}
    >>> (repeat1, repeat2) = ddiff['repetition_change']
    >>> repeat1
    <root[0]>
    >>>
    >>> # But the verbosity level does not change the actual report object.
    >>> # It only changes the textual representaion of the object. We get the actual object here:
    >>> repeat1.repetition
    {'old_repeat': 1, 'new_repeat': 2, 'old_indexes': [3], 'new_indexes': [0, 1]}
    >>> repeat1.t1
    4
    >>> repeat1.t2
    4
    >>> repeat1.up
    <root>

List that contains dictionary (Tree View)
    >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, {1:1, 2:2}]}}
    >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, {1:3}]}}
    >>> ddiff = DeepDiff(t1, t2, view='tree')
    >>> pprint (ddiff, indent = 2)
    { 'dictionary_item_removed': [<root[4]['b'][2][2] t1:2, t2:not present>],
      'values_changed': [<root[4]['b'][2][1] t1:1, t2:3>]}

Sets (Tree View):
    >>> t1 = {1, 2, 8}
    >>> t2 = {1, 2, 3, 5}
    >>> ddiff = DeepDiff(t1, t2, view='tree')
    >>> print(ddiff)
    {'set_item_removed': [<root: t1:8, t2:not present>], 'set_item_added': [<root: t1:not present, t2:3>, <root: t1:not present, t2:5>]}
    >>> # grabbing one item from set_item_removed set which has one item only
    >>> (item,) = ddiff['set_item_removed']
    >>> item.up
    <root t1:{8, 1, 2}, t2:{1, 2, 3, 5}>
    >>> item.up.t1 == t1
    True

Named Tuples (Tree View):
    >>> from collections import namedtuple
    >>> Point = namedtuple('Point', ['x', 'y'])
    >>> t1 = Point(x=11, y=22)
    >>> t2 = Point(x=11, y=23)
    >>> print(DeepDiff(t1, t2, view='tree'))
    {'values_changed': [<root.y t1:22, t2:23>]}

Custom objects (Tree View):
    >>> class ClassA(object):
    ...     a = 1
    ...     def __init__(self, b):
    ...         self.b = b
    ...
    >>> t1 = ClassA(1)
    >>> t2 = ClassA(2)
    >>>
    >>> print(DeepDiff(t1, t2, view='tree'))
    {'values_changed': [<root.b t1:1, t2:2>]}

Object attribute added (Tree View):
    >>> t2.c = "new attribute"
    >>> pprint(DeepDiff(t1, t2, view='tree'))
    {'attribute_added': [<root.c t1:not present, t2:'new attribute'>],
     'values_changed': [<root.b t1:1, t2:2>]}

Approximate decimals comparison (Significant digits after the point) (Tree View):
    >>> t1 = Decimal('1.52')
    >>> t2 = Decimal('1.57')
    >>> DeepDiff(t1, t2, significant_digits=0, view='tree')
    {}
    >>> ddiff = DeepDiff(t1, t2, significant_digits=1, view='tree')
    >>> ddiff
    {'values_changed': [<root t1:Decimal('1.52'), t2:Decimal('1.57')>]}
    >>> (change1,) = ddiff['values_changed']
    >>> change1
    <root t1:Decimal('1.52'), t2:Decimal('1.57')>
    >>> change1.t1
    Decimal('1.52')
    >>> change1.t2
    Decimal('1.57')
    >>> change1.path()
    'root'

Approximate float comparison (Significant digits after the point) (Tree View):
    >>> t1 = [ 1.1129, 1.3359 ]
    >>> t2 = [ 1.113, 1.3362 ]
    >>> ddiff = DeepDiff(t1, t2, significant_digits=3, view='tree')
    >>> ddiff
    {}
    >>> ddiff = DeepDiff(t1, t2, view='tree')
    >>> pprint(ddiff, indent=2)
    { 'values_changed': [<root[0] t1:1.1129, t2:1.113>, <root[1] t1:1.3359, t2:1.3362>]}
    >>> ddiff = DeepDiff(1.23*10**20, 1.24*10**20, significant_digits=1, view='tree')
    >>> ddiff
    {'values_changed': [<root t1:1.23e+20, t2:1.24e+20>]}

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
Note that to_dict will use the text view even if you did the diff in tree view.

Example:
    >>> t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3]}}
    >>> t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world\n\n\nEnd"}}
    >>> ddiff = DeepDiff(t1, t2, view='tree')
    >>> ddiff.to_dict()
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

If you want the original DeepDiff object to be serialized with all the bells and whistles, you can use the to_json_pickle() and to_json_pickle() in order to serialize and deserialize its results into json. Note that json_pickle is unsafe and json pickle dumps from untrusted sources should never be loaded.

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

**Pycon 2016 Talk**
I gave a talk about how DeepDiff does what it does at Pycon 2016.
`Diff it to Dig it Pycon 2016 video <https://www.youtube.com/watch?v=J5r99eJIxF4>`_

And here is more info: http://zepworks.com/blog/diff-it-to-digg-it/


