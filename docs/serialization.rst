:doc:`/index`

.. _serialization_label:

Serialization
=============

.. _to_dict_label:

To Dict
-------

In order to convert the DeepDiff object into a normal Python dictionary, use the to_dict() method.

Example:
    >>> t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3]}}
    >>> t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world\n\n\nEnd"}}
    >>> ddiff = DeepDiff(t1, t2)
    >>> ddiff.to_dict()
    {'type_changes': {"root[4]['b']": {'old_type': <class 'list'>, 'new_type': <class 'str'>, 'old_value': [1, 2, 3], 'new_value': 'world\n\n\nEnd'}}}


Note that you can override the :ref:`view_label` that was originally used to generate the diff here.

Example:
    >>> t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3]}}
    >>> t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world\n\n\nEnd"}}
    >>> ddiff = DeepDiff(t1, t2, view='tree')
    >>> ddiff.to_dict(view_override='text')
    {'type_changes': {"root[4]['b']": {'old_type': <class 'list'>, 'new_type': <class 'str'>, 'old_value': [1, 2, 3], 'new_value': 'world\n\n\nEnd'}}}

.. _to_json_label:

To Json
-------

Dump json of the text view.

In order to do safe json serialization, use the to_json() method.

**Parameters**

default_mapping : dictionary(optional), a dictionary of mapping of different types to json types.

by default DeepDiff converts certain data types. For example Decimals into floats so they can be exported into json.
If you have a certain object type that the json serializer can not serialize it, please pass the appropriate type
conversion through this dictionary.

kwargs: Any other kwargs you pass will be passed on to Python's json.dumps()


Example 1 Serialize custom objects:
    >>> class A:
    ...     pass
    ...
    >>> class B:
    ...     pass
    ...
    >>> t1 = A()
    >>> t2 = B()
    >>> ddiff = DeepDiff(t1, t2)
    >>> ddiff.to_json()
    TypeError: We do not know how to convert <__main__.A object at 0x10648> of type <class '__main__.A'> for json serialization. Please pass the default_mapping parameter with proper mapping of the object to a basic python type.

    >>> default_mapping = {A: lambda x: 'obj A', B: lambda x: 'obj B'}
    >>> ddiff.to_json(default_mapping=default_mapping)
    '{"type_changes": {"root": {"old_type": "A", "new_type": "B", "old_value": "obj A", "new_value": "obj B"}}}'


Example 2:
    >>> t1 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": [1, 2, 3]}}
    >>> t2 = {1: 1, 2: 2, 3: 3, 4: {"a": "hello", "b": "world\n\n\nEnd"}}
    >>> ddiff = DeepDiff(t1, t2, view='tree')
    >>> ddiff.to_json()
    '{"type_changes": {"root[4][\'b\']": {"old_type": "list", "new_type": "str", "old_value": [1, 2, 3], "new_value": "world\\n\\n\\nEnd"}}}'


.. _to_json_pickle_label:

To Json Pickle
--------------

If you want the original DeepDiff object to be serialized with all the bells and whistles, you can use the to_json_pickle() and from_json_pickle() in order to serialize and deserialize its results into json. Note that json_pickle is unsafe and json pickle dumps from untrusted sources should never be loaded. It is recommended not to use this serialization unless you have to.

.. note::
    You need to install the `jsonpickle <https://github.com/jsonpickle/jsonpickle>`_ package to use the to_json_pickle() method.

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


.. _from_json_pickle_label:

From Json Pickle
----------------

Load the diff object from the json pickle dump.
Take a look at the above :ref:`to_json_pickle_label` for an example.


.. _delta_to_flat_rows_label:

Delta Serialize To Flat Rows
----------------------------

Sometimes, it is desired to serialize a :ref:`delta_label` object to a list of flat rows. For example, to store them in relation databases. In that case, you can use the Delta.to_flat_rows to achieve the desired outcome. The rows are named tuples and can be converted to dictionaries using `._asdict()`

    >>> from pprint import pprint
    >>> from deepdiff import DeepDiff, Delta
    >>> t1 = {"key1": "value1"}
    >>> t2 = {"field2": {"key2": "value2"}}
    >>> diff = DeepDiff(t1, t2, verbose_level=2)
    >>> pprint(diff, indent=2)
    { 'dictionary_item_added': {"root['field2']": {'key2': 'value2'}},
      'dictionary_item_removed': {"root['key1']": 'value1'}}
    >>> delta = Delta(diff, bidirectional=True)
    >>> flat_rows = delta.to_flat_rows()
    >>> pprint(flat_rows, indent=2)
    [ FlatDeltaRow(path=['field2', 'key2'], action='dictionary_item_added', value='value2'),
      FlatDeltaRow(path=['key1'], action='dictionary_item_removed', value='value1')]

.. note::
    When converting a delta to flat rows, nested dictionaries that have single keys in them are flattened too.
    Notice that the diff object says

        { 'dictionary_item_added': {"root['field2']": {'key2': 'value2'}}

    but the flat row is:

        FlatDeltaRow(path=['field2', 'key2'], action='dictionary_item_added', value='value2')

    That means, when you recreate the delta from the flat rows, you need to set force=True to apply the delta:

        >>> t1 + delta == t2
        True
        >>> t2 - delta == t1
        True
        >>> delta2 = Delta(flat_rows_list=flat_rows, bidirectional=True)
        >>> t1 + delta2 == t2
        Expected the old value for root['field2']['key2'] to be None but it is not found. Error found on: 'field2'
        False. You may want to set force=True, especially if this delta is created by passing flat_rows_list or flat_dict_list
        >>> t1 + delta
        {'field2': {'key2': 'value2'}}
        >>> t1 + delta2
        {}
        >>> delta2 = Delta(flat_rows_list=flat_rows, bidirectional=True, force=True)  # We need to set force=True
        >>> t1 + delta2
        {'field2': {'key2': 'value2'}}
        >>>



Flat Row Specs:


    class FlatDataAction(str, enum.Enum):
        values_changed = 'values_changed'
        type_changes = 'type_changes'
        set_item_added = 'set_item_added'
        set_item_removed = 'set_item_removed'
        dictionary_item_added = 'dictionary_item_added'
        dictionary_item_removed = 'dictionary_item_removed'
        iterable_item_added = 'iterable_item_added'
        iterable_item_removed = 'iterable_item_removed'
        iterable_item_moved = 'iterable_item_moved'
        iterable_items_inserted = 'iterable_items_inserted'  # opcode
        iterable_items_deleted = 'iterable_items_deleted'  # opcode
        iterable_items_replaced = 'iterable_items_replaced'  # opcode
        iterable_items_equal = 'iterable_items_equal'  # opcode
        attribute_removed = 'attribute_removed'
        attribute_added = 'attribute_added'
        unordered_iterable_item_added = 'unordered_iterable_item_added'
        unordered_iterable_item_removed = 'unordered_iterable_item_removed'


    UnkownValueCode = 'unknown___'


    class FlatDeltaRow(NamedTuple):
        path: List
        action: FlatDataAction
        value: Optional[Any] = UnkownValueCode
        old_value: Optional[Any] = UnkownValueCode
        type: Optional[Any] = UnkownValueCode
        old_type: Optional[Any] = UnkownValueCode
        new_path: Optional[List] = None
        t1_from_index: Optional[int] = None
        t1_to_index: Optional[int] = None
        t2_from_index: Optional[int] = None
        t2_to_index: Optional[int] = None


.. _delta_to_flat_dicts_label:

Delta Serialize To Flat Dictionaries
------------------------------------

Sometimes, it is desired to serialize a :ref:`delta_label` object to a list of flat dictionaries. For example, to store them in relation databases. In that case, you can use the Delta.to_flat_dicts to achieve the desired outcome.

Since None is a valid value, we use a special hard-coded string to signify "unkown": 'unknown___'

.. note::
    Many new keys are added to the flat dicts in DeepDiff 7.0.0
    You may want to use :ref:`delta_to_flat_rows_label` instead of flat dicts.

For example:

    >>> from pprint import pprint
    >>> from deepdiff import DeepDiff, Delta
    >>> t1 = {"key1": "value1"}
    >>> t2 = {"field2": {"key2": "value2"}}
    >>> diff = DeepDiff(t1, t2, verbose_level=2)
    >>> pprint(diff, indent=2)
    { 'dictionary_item_added': {"root['field2']": {'key2': 'value2'}},
      'dictionary_item_removed': {"root['key1']": 'value1'}}
    >>> delta = Delta(diff, bidirectional=True)
    >>> flat_dicts = delta.to_flat_dicts()
    >>> pprint(flat_dicts, indent=2)
    [ { 'action': 'dictionary_item_added',
        'new_path': None,
        'old_type': 'unknown___',
        'old_value': 'unknown___',
        'path': ['field2', 'key2'],
        't1_from_index': None,
        't1_to_index': None,
        't2_from_index': None,
        't2_to_index': None,
        'type': 'unknown___',
        'value': 'value2'},
      { 'action': 'dictionary_item_removed',
        'new_path': None,
        'old_type': 'unknown___',
        'old_value': 'unknown___',
        'path': ['key1'],
        't1_from_index': None,
        't1_to_index': None,
        't2_from_index': None,
        't2_to_index': None,
        'type': 'unknown___',
        'value': 'value1'}]


Example 2:

    >>> t3 = ["A", "B"]
    >>> t4 = ["A", "B", "C", "D"]
    >>> diff = DeepDiff(t3, t4, verbose_level=2)
    >>> pprint(diff, indent=2)
    {'iterable_item_added': {'root[2]': 'C', 'root[3]': 'D'}}
    >>>
    >>> delta = Delta(diff, bidirectional=True)
    >>> flat_dicts = delta.to_flat_dicts()
    >>> pprint(flat_dicts, indent=2)
    [ { 'action': 'iterable_item_added',
        'new_path': None,
        'old_type': 'unknown___',
        'old_value': 'unknown___',
        'path': [2],
        't1_from_index': None,
        't1_to_index': None,
        't2_from_index': None,
        't2_to_index': None,
        'type': 'unknown___',
        'value': 'C'},
      { 'action': 'iterable_item_added',
        'new_path': None,
        'old_type': 'unknown___',
        'old_value': 'unknown___',
        'path': [3],
        't1_from_index': None,
        't1_to_index': None,
        't2_from_index': None,
        't2_to_index': None,
        'type': 'unknown___',
        'value': 'D'}]


.. _delta_from_flat_dicts_label:

Delta Load From Flat Dictionaries
------------------------------------

    >>> from deepdiff import DeepDiff, Delta
    >>> t3 = ["A", "B"]
    >>> t4 = ["A", "B", "C", "D"]
    >>> diff = DeepDiff(t3, t4, verbose_level=2)
    >>> delta = Delta(diff, bidirectional=True)
    >>> flat_dicts = delta.to_flat_dicts()
    >>>
    >>> delta2 = Delta(flat_dict_list=flat_dicts)
    >>> t3 + delta == t4
    True


Back to :doc:`/index`
