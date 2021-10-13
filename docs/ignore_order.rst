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

.. _ignore_order_func_label:

Dynamic Ignore Order
--------------------

Sometimes single *ignore_order* parameter is not enough to do a diff job,
you can use *ignore_order_func* to determine whether the order of certain paths should be ignored

List difference ignoring order with *ignore_order_func*
    >>> t1 = {"set": [1,2,3], "list": [1,2,3]}
    >>> t2 = {"set": [3,2,1], "list": [3,2,1]}
    >>> ddiff = DeepDiff(t1, t2, ignore_order_func=lambda level: "set" in level.path())
    >>> print (ddiff)
    { 'values_changed': { "root['list'][0]": {'new_value': 3, 'old_value': 1},
                          "root['list'][2]": {'new_value': 1, 'old_value': 3}}}


Ignoring order when certain word in the path
    >>> from deepdiff import DeepDiff
    >>> t1 = {'a': [1, 2], 'b': [3, 4]}
    >>> t2 = {'a': [2, 1], 'b': [4, 3]}
    >>> DeepDiff(t1, t2, ignore_order=True)
    {}
    >>> def ignore_order_func(level):
    ...     return 'a' in level.path()
    ...
    >>> DeepDiff(t1, t2, ignore_order=True, ignore_order_func=ignore_order_func)
    {'values_changed': {"root['b'][0]": {'new_value': 4, 'old_value': 3}, "root['b'][1]": {'new_value': 3, 'old_value': 4}}}


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

.. note::
    The definition of pass is whenever 2 iterable objects are being compared with each other and deepdiff decides to compare every single element of one iterable with every single element of the other iterable.
    Refer to :ref:`cutoff_distance_for_pairs_label` and :ref:`cutoff_intersection_for_pairs_label` for more info on how DeepDiff decides to start a new pass.

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
    However the most accurate result might have already been found when there are still potential passes left to be run.

    For example in the above example at max_passes=64, DeepDiff finds the optimal result however it has one more pass
    to go before it has run all the potential passes. Hence just for the sake of example we are using max_passes=65
    as an example of a number that doesn't issue warnings.

.. note::
    Also take a look at :ref:`max_passes_label`

.. _cutoff_distance_for_pairs_label:

Cutoff Distance For Pairs
-------------------------

cutoff_distance_for_pairs : 1 >= float >= 0, default=0.3
    What is the threshold to consider 2 items as potential pairs.
    Note that it is only used when ignore_order = True.

cutoff_distance_for_pairs in combination with :ref:`cutoff_intersection_for_pairs_label` are the parameters that decide whether 2 objects to be paired with each other during ignore_order=True algorithm or not. Note that these parameters are mainly used for nested iterables.

For example by going from the default of cutoff_distance_for_pairs=0.3 to 0.1, we have essentially disallowed the 1.0 and 20.0 to be paired with each other. As you can see, DeepDiff has decided that the :ref:`deep_distance_label` of 1.0 and 20.0 to be around 0.27. Since that is way above cutoff_distance_for_pairs of 0.1, the 2 items are not paired. As a result the lists containing the 2 numbers are directly compared with each other:

    >>> from deepdiff import DeepDiff
    >>> t1 = [[1.0]]
    >>> t2 = [[20.0]]
    >>> DeepDiff(t1, t2, ignore_order=True, cutoff_distance_for_pairs=0.3)
    {'values_changed': {'root[0][0]': {'new_value': 20.0, 'old_value': 1.0}}}
    >>> DeepDiff(t1, t2, ignore_order=True, cutoff_distance_for_pairs=0.1)
    {'values_changed': {'root[0]': {'new_value': [20.0], 'old_value': [1.0]}}}
    >>> DeepDiff(1.0, 20.0, get_deep_distance=True)
    {'values_changed': {'root': {'new_value': 20.0, 'old_value': 1.0}}, 'deep_distance': 0.2714285714285714}


.. _cutoff_intersection_for_pairs_label:

Cutoff Intersection For Pairs
-----------------------------

cutoff_intersection_for_pairs : 1 >= float >= 0, default=0.7
    What is the threshold to calculate pairs of items between 2 iterables.
    For example 2 iterables that have nothing in common, do not need their pairs to be calculated.
    Note that it is only used when ignore_order = True.

Behind the scene DeepDiff takes the :ref:`deep_distance_label` of objects when running ignore_order=True.
The distance is between zero and 1.
A distance of zero means the items are equal. A distance of 1 means they are 100% different.
When comparing iterables, the cutoff_intersection_for_pairs is used to decide whether to compare every single item in each iterable
with every single item in the other iterable or not. If the distance between the 2 iterables is equal or bigger than the
cutoff_intersection_for_pairs, then the 2 iterables items are only compared as added or removed items and NOT modified items.
However, if the distance between 2 iterables is below the cutoff, every single item from each iterable will be compared to every
single item from the other iterable to find the closest "pair" of each item.

.. note::
    The process of comparing every item to the other is very expensive so :ref:`cutoff_intersection_for_pairs_label` in combination with :ref:`cutoff_distance_for_pairs_label` is used to give acceptable results with much higher speed.

With a low cutoff_intersection_for_pairs, the 2 iterables above will be considered too
far off from each other to get the individual pairs of items.
So numbers that are not only related to each other via their positions in the lists
and not their values are paired together in the results.

    >>> t1 = [1.0, 2.0, 3.0, 4.0, 5.0]
    >>> t2 = [5.0, 3.01, 1.2, 2.01, 4.0]
    >>>
    >>> DeepDiff(t1, t2, ignore_order=True, cutoff_intersection_for_pairs=0.1)
    {'values_changed': {'root[1]': {'new_value': 3.01, 'old_value': 2.0}, 'root[2]': {'new_value': 1.2, 'old_value': 3.0}}, 'iterable_item_added': {'root[3]': 2.01}, 'iterable_item_removed': {'root[0]': 1.0}}

With the cutoff_intersection_for_pairs of 0.7 (which is the default value),
the 2 iterables will be considered close enough to get pairs of items between the 2.
So 2.0 and 2.01 are paired together for example.

    >>> t1 = [1.0, 2.0, 3.0, 4.0, 5.0]
    >>> t2 = [5.0, 3.01, 1.2, 2.01, 4.0]
    >>>
    >>> DeepDiff(t1, t2, ignore_order=True, cutoff_intersection_for_pairs=0.7)
    {'values_changed': {'root[2]': {'new_value': 3.01, 'old_value': 3.0}, 'root[0]': {'new_value': 1.2, 'old_value': 1.0}, 'root[1]': {'new_value': 2.01, 'old_value': 2.0}}}


As an example of how much this parameter can affect the results in deeply nested objects, please take a look at :ref:`distance_and_diff_granularity_label`.


.. _iterable_compare_func_label2:

Iterable Compare Func
---------------------

New in DeepDiff 5.5.0

There are times that we want to guide DeepDiff as to what items to compare with other items. In such cases we can pass a `iterable_compare_func` that takes a function pointer to compare two items. The function takes three parameters (x, y, level) and should return `True` if it is a match, `False` if it is not a match or raise `CannotCompare` if it is unable to compare the two.


For example take the following objects:

    >>> from deepdiff import DeepDiff
    >>> from deepdiff.helper import CannotCompare
    >>>
    >>> t1 = [
    ...     {
    ...         'id': 1,
    ...         'value': [1]
    ...     },
    ...     {
    ...         'id': 2,
    ...         'value': [7, 8, 1]
    ...     },
    ...     {
    ...         'id': 3,
    ...         'value': [7, 8],
    ...     },
    ... ]
    >>>
    >>> t2 = [
    ...     {
    ...         'id': 2,
    ...         'value': [7, 8]
    ...     },
    ...     {
    ...         'id': 3,
    ...         'value': [7, 8, 1],
    ...     },
    ...     {
    ...         'id': 1,
    ...         'value': [1]
    ...     },
    ... ]
    >>>
    >>> DeepDiff(t1, t2, ignore_order=True)
    {'values_changed': {"root[2]['id']": {'new_value': 2, 'old_value': 3}, "root[1]['id']": {'new_value': 3, 'old_value': 2}}}


Now let's define a compare_func that takes 3 parameters: x, y and level.

    >>> def compare_func(x, y, level=None):
    ...     try:
    ...         return x['id'] == y['id']
    ...     except Exception:
    ...         raise CannotCompare() from None
    ...
    >>> DeepDiff(t1, t2, ignore_order=True, iterable_compare_func=compare_func)
    {'iterable_item_added': {"root[2]['value'][2]": 1}, 'iterable_item_removed': {"root[1]['value'][2]": 1}}

As you can see the results are different. Now items with the same ids are compared with each other.

.. note::

    The level parameter of the iterable_compare_func is only used when ignore_order=False.

Back to :doc:`/index`
