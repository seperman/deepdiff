**Delta**

DeepDiff Delta is a directed delta that when applied to t1 can yield t2 where delta is the difference of t1 and t2.
Delta objects are like git commits but for structured data.
You can convert the diff results into Delta objects, store the deltas and later apply to other objects.

.. note::
    If you plan to generate Delta objects from the DeepDiff result, and ignore_order=True, you need to also set the report_repetition=True.

**Parameters**

diff : Delta dictionary, Delta dump payload or a DeepDiff object, default=None.
    :ref:`delta_diff_label` is the content to be loaded.

delta_path : String, default=None.
    :ref:`delta_path_label` is the local path to the delta dump file to be loaded

delta_file : File Object, default=None.
    :ref:`delta_file_label` is the file object containing the delta data.

.. note::
    You need to pass only one of the diff, delta_path, or delta_file.

deserializer : Deserializer function, default=pickle_load
    :ref:`delta_deserializer_label` is the function to deserialize the delta content. The default is the pickle_load function that comes with DeepDiff.

serializer : Serializer function, default=pickle_dump
    :ref:`delta_serializer_label` is the function to serialize the delta content into a format that can be stored. The default is the pickle_dump function that comes with DeepDiff.

log_errors : Boolean, default=True
    Whether to log the errors or not.

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

verify_symmetry : Boolean, default=False
    :ref:`delta_verify_symmetry_label` is used to verify that the original value of items are the same as when the delta was created. Note that in order for this option to work, the delta object will need to store more data and thus the size of the object will increase. Let's say that the diff object says root[0] changed value from X to Y. If you create the delta with the default value of verify_symmetry=False, then what delta will store is root[0] = Y. And if this delta was applied to an object that has any root[0] value, it will still set the root[0] to Y. However if verify_symmetry=True, then the delta object will store also that the original value of root[0] was X and if you try to apply the delta to an object that has root[0] of any value other than X, it will notify you.

**Returns**

    A delta object that can be added to t1 to recreate t2.


.. _delta_diff_label:

Diff
----

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


.. _delta_deserializer_label:

Delta Deserializer
------------------

DeepDiff by default uses a restricted Python pickle function to deserialize the Delta dumps. Read more about :ref:`delta_dump_safety_label`.

The user of Delta can decide to switch the serializer and deserializer to their custom ones. The serializer and deserializer parameters can be used exactly for that reason. The best way to come up with your own serializer and deserialier is to take a look at the `pickle_dump and pickle_load functions in the serializer module <https://github.com/seperman/deepdiff/serialization.py>`_


.. _delta_serializer_label:

Delta Serializer
----------------

DeepDiff uses pickle to serialize delta objects by default. Please take a look at the :ref:`delta_deserializer_label` for more information.

.. _delta_dump_safety_label:

Delta Dump Safety
-----------------

Delta by default uses Python's pickle to serialize and deserialize. While the unrestricted use of pickle is not safe as noted in the `pickle's documentation <https://docs.python.org/3/library/pickle.html>`_ , DeepDiff's Delta is written with extra care to `restrict the globals <https://docs.python.org/3/library/pickle.html#restricting-globals>`_ and hence mitigate this security risk.

In fact only a few Python object types are allowed by default. The user of DeepDiff can pass additional types using the :ref:`delta_safe_to_import_label` to allow further object types that need to be allowed.

.. _delta_mutate_label:

Delta Mutate parameter
----------------------

Whether to mutate the original object or not.

.. _delta_and_numpy_label:

Delta and Numpy
---------------

.. note::
    When applying delta to Numpy arrays, make sure to put the delta object first and the numpy array second. This is because Numpy array overrides the + operator and thus DeepDiff's Delta won't be able to be applied.

    >>>

.. note::
    You can not apply a delta that was created from normal Python objects to Numpy arrays.

    >>>


.. _delta_safe_to_import_label:

Delta Safe To Import parameter
------------------------------

.. _delta_verify_symmetry_label:

Delta Verify Symmetry parameter
-------------------------------
