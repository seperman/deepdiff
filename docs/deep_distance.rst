:doc:`/index`

.. _deep_distance_label:

Deep Distance
=============


Deep Distance is the distance between 2 objects. It is a floating point number between 0 and 1. Deep Distance in concept is inspired by `Levenshtein Edit Distance <https://en.wikipedia.org/wiki/Levenshtein_distance>`_.

At its core, the Deep Distance is the number of operations needed to convert one object to the other divided by the sum of the sizes of the 2 objects capped at 1. Note that unlike Levensthtein Distance, the Deep Distance is based on the number of operations and NOT the “minimum” number of operations to convert one object to the other. The number is highly dependent on the granularity of the diff results. And the granularity is controlled by the parameters passed to DeepDiff.

.. _get_deep_distance_label:

Get Deep Distance
-----------------

get_deep_distance: Boolean, default = False
    get_deep_distance will get you the deep distance between objects. The distance is a number between 0 and 1 where zero means there is no diff between the 2 objects and 1 means they are very different. Note that this number should only be used to compare the similarity of 2 objects and nothing more. The algorithm for calculating this number may or may not change in the future releases of DeepDiff.

    The value of Deep Distance will show up in the result diff object's deep_distance key.

    >>> from deepdiff import DeepDiff
    >>> DeepDiff(10.0, 10.1, get_deep_distance=True)
    {'values_changed': {'root': {'new_value': 10.1, 'old_value': 10.0}}, 'deep_distance': 0.0014925373134328302}
    >>> DeepDiff(10.0, 100.1, get_deep_distance=True)
    {'values_changed': {'root': {'new_value': 100.1, 'old_value': 10.0}}, 'deep_distance': 0.24550408719346048}
    >>> DeepDiff(10.0, 1000.1, get_deep_distance=True)
    {'values_changed': {'root': {'new_value': 1000.1, 'old_value': 10.0}}, 'deep_distance': 0.29405999405999406}
    >>> DeepDiff([1], [1], get_deep_distance=True)
    {}
    >>> DeepDiff([1], [1, 2], get_deep_distance=True)
    {'iterable_item_added': {'root[1]': 2}, 'deep_distance': 0.2}
    >>> DeepDiff([1], [1, 2, 3], get_deep_distance=True)
    {'iterable_item_added': {'root[1]': 2, 'root[2]': 3}, 'deep_distance': 0.3333333333333333}
    >>> DeepDiff([[2, 1]], [[1, 2, 3]], ignore_order=True, get_deep_distance=True)
    {'iterable_item_added': {'root[0][2]': 3}, 'deep_distance': 0.1111111111111111}

.. _distance_and_diff_granularity_label:

Distance And Diff Granularity
-----------------------------

.. note::
    Deep Distance of objects are highly dependent on the diff object that is produced. A diff object that is more granular will give more accurate Deep Distance value too.

Let's use the following 2 deeply nested objects as an example. If you ignore the order of items, they are very similar and only differ in a few elements.

We will run 2 diffs and ask for the deep distance. The only difference between the below 2 diffs is that in the first one the :ref:`cutoff_intersection_for_pairs_label` is not passed so the default value of 0.3 is used while in the other one cutoff_intersection_for_pairs=1 is used which forces extra pass calculations.

>>> from pprint import pprint
>>> t1 = [
...     {
...         "key3": [[[[[[[[[[1, 2, 4, 5]]], [[[8, 7, 3, 5]]]]]]]]]],
...         "key4": [7, 8]
...     },
...     {
...         "key5": "val5",
...         "key6": "val6"
...     }
... ]
>>>
>>> t2 = [
...     {
...         "key5": "CHANGE",
...         "key6": "val6"
...     },
...     {
...         "key3": [[[[[[[[[[1, 3, 5, 4]]], [[[8, 8, 1, 5]]]]]]]]]],
...         "key4": [7, 8]
...     }
... ]

We don't pass cutoff_intersection_for_pairs in the first diff.

>>> diff1=DeepDiff(t1, t2, ignore_order=True, cache_size=5000, get_deep_distance=True)
>>> pprint(diff1)
{'deep_distance': 0.36363636363636365,
 'values_changed': {'root[0]': {'new_value': {'key5': 'CHANGE', 'key6': 'val6'},
                                'old_value': {'key3': [[[[[[[[[[1, 2, 4, 5]]],
                                                             [[[8,
                                                                7,
                                                                3,
                                                                5]]]]]]]]]],
                                              'key4': [7, 8]}},
                    'root[1]': {'new_value': {'key3': [[[[[[[[[[1, 3, 5, 4]]],
                                                             [[[8,
                                                                8,
                                                                1,
                                                                5]]]]]]]]]],
                                              'key4': [7, 8]},
                                'old_value': {'key5': 'val5', 'key6': 'val6'}}}}

Note that the stats show that only 5 set of objects were compared with each other according to the DIFF COUNT:

>>> diff1.get_stats()
{'PASSES COUNT': 0, 'DIFF COUNT': 5, 'DISTANCE CACHE HIT COUNT': 0, 'MAX PASS LIMIT REACHED': False, 'MAX DIFF LIMIT REACHED': False}

Let's pass cutoff_intersection_for_pairs=1 to enforce pass calculations. As you can see the results are way more granular and the deep distance value is way more accurate now.

>>> diff2=DeepDiff(t1, t2, ignore_order=True, cache_size=5000, cutoff_intersection_for_pairs=1, get_deep_distance=True)
>>> from pprint import pprint
>>> pprint(diff2)
{'deep_distance': 0.06060606060606061,
 'iterable_item_removed': {"root[0]['key3'][0][0][0][0][0][0][1][0][0][1]": 7},
 'values_changed': {"root[0]['key3'][0][0][0][0][0][0][0][0][0][1]": {'new_value': 3,
                                                                      'old_value': 2},
                    "root[0]['key3'][0][0][0][0][0][0][1][0][0][2]": {'new_value': 1,
                                                                      'old_value': 3},
                    "root[1]['key5']": {'new_value': 'CHANGE',
                                        'old_value': 'val5'}}}

As you can see now way more calculations have happened behind the scene. Instead of only 5 set of items being compared with each other, we have 306 items that are compared with each other in 110 passes.

>>> diff2.get_stats()
{'PASSES COUNT': 110, 'DIFF COUNT': 306, 'DISTANCE CACHE HIT COUNT': 0, 'MAX PASS LIMIT REACHED': False, 'MAX DIFF LIMIT REACHED': False}


Back to :doc:`/index`
