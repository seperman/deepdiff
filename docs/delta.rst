.. _delta_label:

Delta
=====

DeepDiff Delta is a directed delta that when applied to t1 can yield t2 where delta is the difference between t1 and t2.
Delta objects are like git commits but for structured data.
You can convert the diff results into Delta objects, store the deltas, and later apply to other objects.

.. note::
    If you plan to generate Delta objects from the DeepDiff result, and ignore_order=True, you need to also set the report_repetition=True.

**Parameters**

diff : Delta dictionary, Delta dump payload or a DeepDiff object, default=None.
    :ref:`delta_diff_label` is the content to be loaded.

delta_path : String, default=None.
    :ref:`delta_path_label` is the local path to the delta dump file to be loaded

delta_file : File Object, default=None.
    :ref:`delta_file_label` is the file object containing the delta data.

delta_diff : Delta diff, default=None.
    This is a slightly different diff than the output of DeepDiff. When Delta object is initiated from the DeepDiff output, it transforms the diff into a slightly different structure that is more suitable for delta. You can find that object via delta.diff.
    It is the same object that is serialized when you create a delta dump. If you already have the delta_diff object, you can pass it to Delta via the delta_diff parameter.

flat_dict_list : List of flat dictionaries, default=None,
    :ref:`flat_dict_list_label` can be used to load the delta object from a list of flat dictionaries.

.. note::
    You need to pass only one of the diff, delta_path, or delta_file parameters.

deserializer : Deserializer function, default=pickle_load
    :ref:`delta_deserializer_label` is the function to deserialize the delta content. The default is the pickle_load function that comes with DeepDiff.

serializer : Serializer function, default=pickle_dump
    :ref:`delta_serializer_label` is the function to serialize the delta content into a format that can be stored. The default is the pickle_dump function that comes with DeepDiff.

log_errors : Boolean, default=True
    Whether to log the errors or not when applying the delta object.

raise_errors : Boolean, default=False
    :ref:`raise_errors_label`
    Whether to raise errors or not when applying a delta object.

mutate : Boolean, default=False.
    :ref:`delta_mutate_label` defines whether to mutate the original object when adding the delta to it or not.
    Note that this parameter is not always successful in mutating. For example if your original object
    is an immutable type such as a frozenset or a tuple, mutation will not succeed.
    Hence it is recommended to keep this parameter as the default value of False unless you are sure
    that you do not have immutable objects. There is a small overhead of doing deepcopy on the original
    object when mutate=False. If performance is a concern and modifying the original object is not a big deal,
    set the mutate=True but always reassign the output back to the original object.

safe_to_import : Set, default=None.
    :ref:`delta_safe_to_import_label` is a set of modules that needs to be explicitly white listed to be loaded
    Example: {'mymodule.MyClass', 'decimal.Decimal'}
    Note that this set will be added to the basic set of modules that are already white listed.
    The set of what is already white listed can be found in deepdiff.serialization.SAFE_TO_IMPORT

bidirectional : Boolean, default=False
    :ref:`delta_verify_symmetry_label` is used to verify that the original value of items are the same as when the delta was created. Note that in order for this option to work, the delta object will need to store more data and thus the size of the object will increase. Let's say that the diff object says root[0] changed value from X to Y. If you create the delta with the default value of bidirectional=False, then what delta will store is root[0] = Y. And if this delta was applied to an object that has any root[0] value, it will still set the root[0] to Y. However if bidirectional=True, then the delta object will store also that the original value of root[0] was X and if you try to apply the delta to an object that has root[0] of any value other than X, it will notify you.

force : Boolean, default=False
    :ref:`delta_force_label` is used to force apply a delta to objects that have a different structure than what the delta was originally created from.

always_include_values : Boolean, default=False
    :ref:`always_include_values_label` is used to make sure the delta objects includes the values that were changed. Sometime Delta tries to be efficient not include the values when it can get away with it. By setting this parameter to True, you ensure that the Delta object will include the values.


**Returns**

    A delta object that can be added to t1 to recreate t2.

    Delta objects can contain the following vocabulary:

    iterable_item_added
    iterable_item_moved
    iterable_item_removed
    set_item_added
    set_item_removed
    dictionary_item_added
    dictionary_item_removed
    attribute_added
    attribute_removed
    type_changes
    values_changed
    iterable_items_added_at_indexes
    iterable_items_removed_at_indexes


.. _delta_diff_label:

Diff to load in Delta
---------------------

diff : Delta dictionary, Delta dump payload or a DeepDiff object, default=None.
    diff is the content to be loaded.

>>> from deepdiff import DeepDiff, Delta
>>> from pprint import pprint
>>>
>>> t1 = [1, 2, 3]
>>> t2 = ['a', 2, 3, 4]
>>> diff = DeepDiff(t1, t2)
>>> diff
{'type_changes': {'root[0]': {'old_type': <class 'int'>, 'new_type': <class 'str'>, 'old_value': 1, 'new_value': 'a'}}, 'iterable_item_added': {'root[3]': 4}}
>>> delta = Delta(diff)
>>> delta
<Delta: {'type_changes': {'root[0]': {'old_type': <class 'int'>, 'new_type': <class 'str'>, 'new_value': ...}>

Applying the delta object to t1 will yield t2:

>>> t1 + delta
['a', 2, 3, 4]
>>> t1 + delta == t2
True

If we want to subtract a delta, we need to create a bidirectional delta:

>>> delta = Delta(diff, bidirectional=True)
>>> t2 - delta
[1, 2, 3]
>>> t2 - delta == t1
True

Now let's dump the delta object so we can store it.

>>> dump = delta.dumps()
>>>
>>> dump
b'\x80\x04\x95\x8d\x00\x00\x00\x00\x00\x00\x00}\x94(\x8c\x0ctype_changes\x94}\x94\x8c\x07root[0]\x94}\x94(\x8c\x08old_type\x94\x8c\x08builtins\x94\x8c\x03int\x94\x93\x94\x8c\x08new_type\x94h\x06\x8c\x03str\x94\x93\x94\x8c\tnew_value\x94\x8c\x01a\x94us\x8c\x13iterable_item_added\x94}\x94\x8c\x07root[3]\x94K\x04su.'

The dumps() function gives us the serialized content of the delta in the form of bytes. We could store it however we want. Or we could use the dump(file_object) to write the dump to the file_object instead. But before we try the dump(file_object) method, let's create a new Delta object and reapply it to t1 and see if we still get t2:

>>> delta2 = Delta(dump)
>>> t1 + delta2 == t2
True
>>>

.. _delta_path_label:

Delta Path parameter
--------------------

Ok now we can try the dumps(file_object). It does what you expect:

>>> with open('/tmp/delta1', 'wb') as dump_file:
...     delta.dump(dump_file)
...

And we use the delta_path parameter to load the delta

>>> delta3 = Delta(delta_path='/tmp/delta1')

It still gives us the same result when applied.

>>> t1 + delta3 == t2
True


.. _delta_file_label:

Delta File parameter
--------------------

You can also pass a file object containing the delta dump:

>>> with open('/tmp/delta1', 'rb') as dump_file:
...     delta4 = Delta(delta_file=dump_file)
...
>>> t1 + delta4 == t2
True


.. _flat_dict_list_label:

Flat Dict List
--------------

You can create a delta object from the list of flat dictionaries that are produced via :ref:`to_flat_dicts_label`. Read more on :ref:`delta_from_flat_dicts_label`.

.. _flat_rows_list_label:

Flat Rows List
--------------

You can create a delta object from the list of flat dictionaries that are produced via :ref:`to_flat_rows_label`. Read more on :ref:`delta_from_flat_rows_label`.


.. _delta_deserializer_label:

Delta Deserializer
------------------

DeepDiff by default uses a restricted Python pickle function to deserialize the Delta dumps. Read more about :ref:`delta_dump_safety_label`.

The user of Delta can decide to switch the serializer and deserializer to their custom ones. The serializer and deserializer parameters can be used exactly for that reason. The best way to come up with your own serializer and deserialier is to take a look at the `pickle_dump and pickle_load functions in the serializer module <https://github.com/seperman/deepdiff/serialization.py>`_

.. _delta_json_deserializer_label:

Json Deserializer for Delta
```````````````````````````

If all you deal with are Json serializable objects, you can use json for serialization.

>>> from deepdiff import DeepDiff, Delta
>>> from deepdiff.serialization import json_dumps, json_loads
>>> t1 = {"a": 1}
>>> t2 = {"a": 2}
>>>
>>> diff = DeepDiff(t1, t2)
>>> delta = Delta(diff, serializer=json_dumps)
>>> dump = delta.dumps()
>>> dump
'{"values_changed":{"root[\'a\']":{"new_value": 2}}}'
>>> delta_reloaded = Delta(dump, deserializer=json_loads)
>>> t2 == delta_reloaded + t1
True


.. note::

    Json is very limited and easily you can get to deltas that are not json serializable. You will probably want to extend the Python's Json serializer to support your needs.

    >>> import json
    >>> t1 = {"a": 1}
    >>> t2 = {"a": None}
    >>> diff = DeepDiff(t1, t2)
    >>> diff
    {'type_changes': {"root['a']": {'old_type': <class 'int'>, 'new_type': <class 'NoneType'>, 'old_value': 1, 'new_value': None}}}
    >>> Delta(diff, serializer=json.dumps)
    <Delta: {'type_changes': {"root['a']": {'old_type': <class 'int'>, 'new_type': <class 'NoneType'>, 'new_v...}>
    >>> delta = Delta(diff, serializer=json.dumps)
    >>> dump = delta.dumps()
    Traceback (most recent call last):
      File "lib/python3.8/json/encoder.py", line 179, in default
        raise TypeError(f'Object of type {o.__class__.__name__} '
    TypeError: Object of type type is not JSON serializable

.. _delta_serializer_label:

Delta Serializer
----------------

DeepDiff uses pickle to serialize delta objects by default. Please take a look at the :ref:`delta_deserializer_label` for more information.


.. _to_flat_dicts_label:

Delta Serialize To Flat Dictionaries
------------------------------------

Read about :ref:`delta_to_flat_dicts_label`

.. _delta_dump_safety_label:

Delta Dump Safety
-----------------

Delta by default uses Python's pickle to serialize and deserialize. While the unrestricted use of pickle is not safe as noted in the `pickle's documentation <https://docs.python.org/3/library/pickle.html>`_ , DeepDiff's Delta is written with extra care to `restrict the globals <https://docs.python.org/3/library/pickle.html#restricting-globals>`_ and hence mitigate this security risk.

In fact only a few Python object types are allowed by default. The user of DeepDiff can pass additional types using the :ref:`delta_safe_to_import_label` to allow further object types that need to be allowed.


.. _delta_mutate_label:

Delta Mutate parameter
----------------------

mutate : Boolean, default=False.
    delta_mutate defines whether to mutate the original object when adding the delta to it or not.
    Note that this parameter is not always successful in mutating. For example if your original object
    is an immutable type such as a frozenset or a tuple, mutation will not succeed.
    Hence it is recommended to keep this parameter as the default value of False unless you are sure
    that you do not have immutable objects. There is a small overhead of doing deepcopy on the original
    object when mutate=False. If performance is a concern and modifying the original object is not a big deal,
    set the mutate=True but always reassign the output back to the original object.

For example:

>>> t1 = [1, 2, [3, 5, 6]]
>>> t2 = [2, 3, [3, 6, 8]]

>>> diff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True)
>>> diff
{'values_changed': {'root[0]': {'new_value': 3, 'old_value': 1}, 'root[2][1]': {'new_value': 8, 'old_value': 5}}}
>>> delta = Delta(diff)
>>> delta
<Delta: {'values_changed': {'root[0]': {'new_value': 3}, 'root[2][1]': {'new_value': 8}}}>

Note that we can apply delta to objects different than the original objects they were made from:

>>> t3 = ["a", 2, [3, "b", "c"]]
>>> t3 + delta
[3, 2, [3, 8, 'c']]

If we check t3, it is still the same as the original value of t3:

>>> t3
['a', 2, [3, 'b', 'c']]

Now let's make the delta with mutate=True

>>> delta2 = Delta(diff, mutate=True)
>>> t3 + delta2
[3, 2, [3, 8, 'c']]
>>> t3
[3, 2, [3, 8, 'c']]

Applying the delta to t3 mutated the t3 itself in this case!


.. _delta_and_numpy_label:

Delta and Numpy
---------------

>>> from deepdiff import DeepDiff, Delta
>>> import numpy as np
>>> t1 = np.array([1, 2, 3, 5])
>>> t2 = np.array([2, 2, 7, 5])
>>> diff = DeepDiff(t1, t2)
>>> diff
{'values_changed': {'root[0]': {'new_value': 2, 'old_value': 1}, 'root[2]': {'new_value': 7, 'old_value': 3}}}
>>> delta = Delta(diff)

.. note::
    When applying delta to Numpy arrays, make sure to put the delta object first and the numpy array second. This is because Numpy array overrides the + operator and thus DeepDiff's Delta won't be able to be applied.

    >>> t1 + delta
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
        raise DeltaNumpyOperatorOverrideError(DELTA_NUMPY_OPERATOR_OVERRIDE_MSG)
    deepdiff.delta.DeltaNumpyOperatorOverrideError: A numpy ndarray is most likely being added to a delta. Due to Numpy override the + operator, you can only do: delta + ndarray and NOT ndarray + delta

Let's put the delta first then:

>>> delta + t1
array([2, 2, 7, 5])
>>> delta + t2 == t2
array([ True,  True,  True,  True])


.. note::
    You can apply a delta that was created from normal Python objects to Numpy arrays. But it is not recommended.

.. _raise_errors_label:

Delta Raise Errors parameter
----------------------------

raise_errors : Boolean, default=False
    Whether to raise errors or not when applying a delta object.

>>> from deepdiff import DeepDiff, Delta
>>> t1 = [1, 2, [3, 5, 6]]
>>> t2 = [2, 3, [3, 6, 8]]
>>> diff = DeepDiff(t1, t2, ignore_order=True, report_repetition=True)
>>> delta = Delta(diff, raise_errors=False)

Now let's apply the delta to a very different object:

>>> t3 = [1, 2, 3, 5]
>>> t4 = t3 + delta
Unable to get the item at root[2][1]

We get the above log message that it was unable to get the item at root[2][1]. We get the message since by default log_errors=True

Let's see what t4 is now:

>>> t4
[3, 2, 3, 5]

So the delta was partially applied on t3.

Now let's set the raise_errors=True

>>> delta2 = Delta(diff, raise_errors=True)
>>>
>>> t3 + delta2
Unable to get the item at root[2][1]
Traceback (most recent call last):
current_old_value = obj[elem]
TypeError: 'int' object is not subscriptable
During handling of the above exception, another exception occurred:
deepdiff.delta.DeltaError: Unable to get the item at root[2][1]


.. _delta_safe_to_import_label:

Delta Safe To Import parameter
------------------------------

safe_to_import : Set, default=None.
    safe_to_import is a set of modules that needs to be explicitly white listed to be loaded
    Example: {'mymodule.MyClass', 'decimal.Decimal'}
    Note that this set will be added to the basic set of modules that are already white listed.


As noted in :ref:`delta_dump_safety_label` and :ref:`delta_deserializer_label`, DeepDiff's Delta takes safety very seriously and thus limits the globals that can be deserialized when importing. However on occasions that you need a specific type (class) that needs to be used in delta objects, you need to pass it to the Delta via safe_to_import parameter.

The set of what is already white listed can be found in deepdiff.serialization.SAFE_TO_IMPORT
At the time of writing this document, this list consists of:

>>> from deepdiff.serialization import SAFE_TO_IMPORT
>>> from pprint import pprint
>>> pprint(SAFE_TO_IMPORT)
{'builtins.None',
 'builtins.bin',
 'builtins.bool',
 'builtins.bytes',
 'builtins.complex',
 'builtins.dict',
 'builtins.float',
 'builtins.frozenset',
 'builtins.int',
 'builtins.list',
 'builtins.range',
 'builtins.set',
 'builtins.slice',
 'builtins.str',
 'builtins.tuple',
 'collections.OrderedDict',
 'collections.namedtuple',
 'datetime.datetime',
 'datetime.time',
 'datetime.timedelta',
 'decimal.Decimal',
 'ordered_set.OrderedSet',
 'orderly_set.sets.SetOrdered',
 're.Pattern',
 'uuid.UUID'}

If you want to pass any other argument to safe_to_import, you will need to put the full path to the type as it appears in the sys.modules

For example let's say you have a package call mypackage and has a module called mymodule. If you check the sys.modules, the address to this module must be mypackage.mymodule. In order for Delta to be able to serialize this object via pickle, first of all it has to be `picklable <https://docs.python.org/3/library/pickle.html#object.__reduce__>`_. 

>>> diff = DeepDiff(t1, t2)
>>> delta = Delta(diff)
>>> dump = delta.dumps()

The dump at this point is serialized via Pickle and can be written to disc if needed.

Later when you want to load this dump, by default Delta will block you from importing anything that is NOT in deepdiff.serialization.SAFE_TO_IMPORT . In fact it will show you this error message when trying to load this dump:

    deepdiff.serialization.ForbiddenModule: Module 'builtins.type' is forbidden. You need to explicitly pass it by passing a safe_to_import parameter

In order to let Delta know that this specific module is safe to import, you will need to pass it to Delta during loading of this dump:

>>> delta = Delta(dump, safe_to_import={'mypackage.mymodule'})

.. note ::

    If you pass a custom deserializer to Delta, DeepDiff will pass safe_to_import parameter to the custom deserializer if that deserializer takes safe_to_import as a parameter in its definition.
    For example if you just use json.loads as deserializer, the safe_to_import items won't be passed to it since json.loads does not have such a parameter.


.. _delta_verify_symmetry_label:

Delta Verify Symmetry parameter
-------------------------------

bidirectional : Boolean, default=False
    bidirectional is used to to include all the required information so that we can use the delta object both for addition and subtraction. It will also check that the object you are adding the delta to, has the same values as the original object that the delta was created from.

    It complains if the object is not what it expected to be.


>>> from deepdiff import DeepDiff, Delta
>>> t1 = [1]
>>> t2 = [2]
>>> t3 = [3]
>>>
>>> diff = DeepDiff(t1, t2)
>>>
>>> delta2 = Delta(diff, raise_errors=False, bidirectional=True)
>>> t4 = delta2 + t3
Expected the old value for root[0] to be 1 but it is 3. Error found on: while checking the symmetry of the delta. You have applied the delta to an object that has different values than the original object the delta was made from
>>> t4
[2]

And if you had set raise_errors=True, then it would have raised the error in addition to logging it.


.. _delta_force_label:

Delta Force
-----------

force : Boolean, default=False
    force is used to force apply a delta to objects that have a different structure than what the delta was originally created from.


>>> from deepdiff import DeepDiff, Delta
>>> t1 = {
...     'x': {
...         'y': [1, 2, 3]
...     },
...     'q': {
...         'r': 'abc',
...     }
... }
>>>
>>> t2 = {
...     'x': {
...         'y': [1, 2, 3, 4]
...     },
...     'q': {
...         'r': 'abc',
...         't': 0.5,
...     }
... }
>>>
>>> diff = DeepDiff(t1, t2)
>>> diff
{'dictionary_item_added': [root['q']['t']], 'iterable_item_added': {"root['x']['y'][3]": 4}}
>>> delta = Delta(diff)
>>> {} + delta
Unable to get the item at root['x']['y'][3]: 'x'
Unable to get the item at root['q']['t']
{}

Once we set the force to be True

>>> delta = Delta(diff, force=True)
>>> {} + delta
{'x': {'y': {3: 4}}, 'q': {'t': 0.5}}

Notice that the force attribute does not know the original object at ['x']['y'] was supposed to be a list, so it assumes it was a dictionary.


.. _always_include_values_label:

Always Include Values
---------------------

always_include_values is used to make sure the delta objects includes the values that were changed. Sometime Delta tries to be efficient not include the values when it can get away with it. By setting this parameter to True, you ensure that the Delta object will include the values.

For example, when the type of an object changes, if we can easily convert from one type to the other, the Delta object does not include the values:


>>> from deepdiff import DeepDiff, Delta
>>> diff = DeepDiff(t1=[1, 2], t2=[1, '2'])
>>> diff
{'type_changes': {'root[1]': {'old_type': <class 'int'>, 'new_type': <class 'str'>, 'old_value': 2, 'new_value': '2'}}}
>>> delta=Delta(diff)
>>> delta
<Delta: {'type_changes': {'root[1]': {'old_type': <class 'int'>, 'new_type': <class 'str'>}}}>

As you can see the delta object does not include the values that were changed. Now let's pass always_include_values=True:

>>> delta=Delta(diff, always_include_values=True)
>>> delta.diff
{'type_changes': {'root[1]': {'old_type': <class 'int'>, 'new_type': <class 'str'>, 'new_value': '2'}}}

If we want to make sure the old values stay with delta, we pass bidirectional=True. By doing so we can also use the delta object to subtract from other objects. 

>>> delta=Delta(diff, always_include_values=True, bidirectional=True)
>>> delta.diff
{'type_changes': {'root[1]': {'old_type': <class 'int'>, 'new_type': <class 'str'>, 'old_value': 2, 'new_value': '2'}}}

