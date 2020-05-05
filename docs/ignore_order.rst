:doc:`/index`

.. _ignore_order_label:

Ignore Order
============

DeepDiff by default compares objects in the order that it iterates through them in iterables.
In other words if you have 2 lists, then the first item of the lists are compared to each other, then the 2nd items and so on.
That makes DeepDiff be able to run in linear time.

However, There are often times when you don't care about the order in which the items have appeared.
In such cases DeepDiff needs to do way more work in order to find the differences.

There are a couple of parameters provided to you to have full control over.


List difference with ignore_order=False which is the default:
    >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
    >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 3, 2, 3]}}
    >>> ddiff = DeepDiff(t1, t2)
    >>> pprint (ddiff, indent = 2)
    { 'iterable_item_added': {"root[4]['b'][3]": 3},
      'values_changed': { "root[4]['b'][1]": {'new_value': 3, 'old_value': 2},
                          "root[4]['b'][2]": {'new_value': 2, 'old_value': 3}}}

Ignore Order
------------

List difference ignoring order or duplicates: (with the same dictionaries as above)
    >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3]}}
    >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 3, 2, 3]}}
    >>> ddiff = DeepDiff(t1, t2, ignore_order=True)
    >>> print (ddiff)
    {}


.. _report_repetition_label:

Reporting Repetitions
---------------------

List difference ignoring order and reporting repetitions:
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

.. _max_passes_label:

Max Passes
----------

max_passes: Integer, default = 10000000
    Maximum number of passes to run on objects to pin point what exactly is different. This is only used when ignore_order=True

If you have deeply nested objects, DeepDiff needs to run multiple passes in order to pin point the difference.
That can dramatically increase the time spent to find the difference.
You can control the maximum number of passes that can be run via the max_passes parameter.

Note: The definition of pass is whenever 2 objects are being compared with each other.

Max Passes Example
    >>> from pprint import pprint
    >>> from deepdiff import DeepDiff
    >>> 
    >>> t1 = [
    ...     {
    ...         'key3': [[[[[1, 2, 4, 5]]]]],
    ...         'key4': [7, 8],
    ...     },
    ...     {
    ...         'key5': 'val5',
    ...         'key6': 'val6',
    ...     },
    ... ]
    >>> 
    >>> t2 = [
    ...     {
    ...         'key5': 'CHANGE',
    ...         'key6': 'val6',
    ...     },
    ...     {
    ...         'key3': [[[[[1, 3, 5, 4]]]]],
    ...         'key4': [7, 8],
    ...     },
    ... ]
    >>> 
    >>> for max_passes in (1, 2, 62, 65):
    ...     diff = DeepDiff(t1, t2, ignore_order=True, max_passes=max_passes, verbose_level=2)
    ...     print('-\n----- Max Passes = {} -----'.format(max_passes))
    ...     pprint(diff)
    ... 
    DeepDiff has reached the max number of passes of 1. You can possibly get more accurate results by increasing the max_passes parameter.
    -
    ----- Max Passes = 1 -----
    {'values_changed': {'root[0]': {'new_value': {'key5': 'CHANGE', 'key6': 'val6'},
                                    'old_value': {'key3': [[[[[1, 2, 4, 5]]]]],
                                                  'key4': [7, 8]}},
                        'root[1]': {'new_value': {'key3': [[[[[1, 3, 5, 4]]]]],
                                                  'key4': [7, 8]},
                                    'old_value': {'key5': 'val5', 'key6': 'val6'}}}}
    DeepDiff has reached the max number of passes of 2. You can possibly get more accurate results by increasing the max_passes parameter.
    -
    ----- Max Passes = 2 -----
    {'values_changed': {"root[0]['key3'][0]": {'new_value': [[[[1, 3, 5, 4]]]],
                                               'old_value': [[[[1, 2, 4, 5]]]]},
                        "root[1]['key5']": {'new_value': 'CHANGE',
                                            'old_value': 'val5'}}}
    DeepDiff has reached the max number of passes of 62. You can possibly get more accurate results by increasing the max_passes parameter.
    -
    ----- Max Passes = 62 -----
    {'values_changed': {"root[0]['key3'][0][0][0][0]": {'new_value': [1, 3, 5, 4],
                                                        'old_value': [1, 2, 4, 5]},
                        "root[1]['key5']": {'new_value': 'CHANGE',
                                            'old_value': 'val5'}}}
    DeepDiff has reached the max number of passes of 65. You can possibly get more accurate results by increasing the max_passes parameter.
    -
    ----- Max Passes = 65 -----
    {'values_changed': {"root[0]['key3'][0][0][0][0][1]": {'new_value': 3,
                                                           'old_value': 2},
                        "root[1]['key5']": {'new_value': 'CHANGE',
                                            'old_value': 'val5'}}}


.. note::
    If there are potential passes left to be run and the max_passes value is reached, DeepDiff will issue a warning.
    However the most accurate result might have been found even before all the potential passes are run.

    For example in the above example at max_passes=64, DeepDiff finds the optimal result however it has one more pass
    to go before it has run all the potential passes. Hence just for the sake of example we are using max_passes=65
    as an example of a number that doesn't issue warnings.

.. note::
    If you plan to generate Delta objects from the DeepDiff result, and ignore_order=True, you need to also set the report_repetition=True.

Back to :doc:`/index`
