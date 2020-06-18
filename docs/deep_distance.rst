:doc:`/index`

.. _deep_distance_label:

Deep Distance
=============

The distance between 2 objects. A number between 0 and 1.
Deep Distance in concept is inspired by Levenshtein Edit distance. At its core, the Deep Distance is the number of operations needed to convert one object to the other divided by the sum of the sizes of the 2 objects. Then the number is capped at 1.

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


Back to :doc:`/index`
