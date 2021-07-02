:doc:`/index`

Other Parameters
================

.. _iterable_compare_func_label:

Iterable Compare Func
---------------------

New in DeepDiff 5.5.0

There are times that we want to guide DeepDiff as to what items to compare with other items. In such cases we can pass a `iterable_compare_func` that takes a function pointer to compare two items. The function takes three parameters (x, y, level) and should return `True` if it is a match, `False` if it is not a match or raise `CannotCompare` if it is unable to compare the two.


For example take the following objects:


Now let's define a compare_func that takes 3 parameters: x, y and level.

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
    >>> DeepDiff(t1, t2)
    {'values_changed': {"root[0]['id']": {'new_value': 2, 'old_value': 1}, "root[0]['value'][0]": {'new_value': 7, 'old_value': 1}, "root[1]['id']": {'new_value': 3, 'old_value': 2}, "root[2]['id']": {'new_value': 1, 'old_value': 3}, "root[2]['value'][0]": {'new_value': 1, 'old_value': 7}}, 'iterable_item_added': {"root[0]['value'][1]": 8}, 'iterable_item_removed': {"root[2]['value'][1]": 8}}

As you can see the results are different. Now items with the same ids are compared with each other.

    >>> def compare_func(x, y, level=None):
    ...     try:
    ...         return x['id'] == y['id']
    ...     except Exception:
    ...         raise CannotCompare() from None
    ...
    >>> DeepDiff(t1, t2, iterable_compare_func=compare_func)
    {'iterable_item_added': {"root[2]['value'][2]": 1}, 'iterable_item_removed': {"root[1]['value'][2]": 1}}

If we set the verbose_level=2, we can see more details.

    >>> DeepDiff(t1, t2, iterable_compare_func=compare_func, verbose_level=2)
    {'iterable_item_added': {"root[2]['value'][2]": 1}, 'iterable_item_removed': {"root[1]['value'][2]": 1}, 'iterable_item_moved': {'root[0]': {'new_path': 'root[2]', 'value': {'id': 1, 'value': [1]}}, 'root[1]': {'new_path': 'root[0]', 'value': {'id': 2, 'value': [7, 8]}}, 'root[2]': {'new_path': 'root[1]', 'value': {'id': 3, 'value': [7, 8, 1]}}}}


We can also use the level parameter. Levels are explained in the :ref:`tree_view_label`.

For example you could use the level object to further determine if the 2 objects should be matches or not.


    >>> t1 = {
    ...     'path1': [],
    ...     'path2': [
    ...         {
    ...             'id': 1,
    ...             'value': [1]
    ...         },
    ...         {
    ...             'id': 2,
    ...             'value': [7, 8, 1]
    ...         },
    ...     ]
    ... }
    >>>
    >>> t2 = {
    ...     'path1': [{'pizza'}],
    ...     'path2': [
    ...         {
    ...             'id': 2,
    ...             'value': [7, 8, 1]
    ...         },
    ...         {
    ...             'id': 1,
    ...             'value': [1, 2]
    ...         },
    ...     ]
    ... }
    >>>
    >>>
    >>> def compare_func2(x, y, level):
    ...     if (not isinstance(x, dict) or not isinstance(y, dict)):
    ...         raise CannotCompare
    ...     if(level.path() == "root['path2']"):
    ...         if (x["id"] == y["id"]):
    ...             return True
    ...         return False
    ...
    >>>
    >>> DeepDiff(t1, t2, iterable_compare_func=compare_func2)
    {'iterable_item_added': {"root['path1'][0]": {'pizza'}, "root['path2'][0]['value'][1]": 2}}


.. note::

    The level parameter of the iterable_compare_func is only used when ignore_order=False which is the default value for ignore_order.

.. _custom_operators_label:

Custom Operators
---------------------

Whether two objects are different or not are largely depend on the context. For example, apple and banana are the same
if you are considering whether the

*custom_operators* is for the job.

To define an custom operator, you just need to inherit a *BaseOperator* and
    * implement method
        * diff(level: DiffLevel, instance: DeepDiff) -> boolean
    * to do custom diff logic with full access to DeepDiff instance
        * you can use instance.custom_report_result to record info
        * to return a boolean value to determine whether the process
          should quit or continue with default behavior


An operator that mapping L2:distance as diff criteria
    >>> from deepdiff import DeepDiff
    >>> from deepdiff.operator import BaseOperator
    >>>
    >>> t1 = {
    ...     "coordinates": [
    ...         {"x": 5, "y": 5},
    ...         {"x": 8, "y": 8}
    ...     ]
    ... }
    ...
    >>> t2 = {
    ...     "coordinates": [
    ...         {"x": 6, "y": 6},
    ...         {"x": 88, "y": 88}
    ...     ]
    ... }
    ...
    >>> class L2DistanceDifferWithPreventDefault(BaseOperator):
    ...     def __init__(self, distance_threshold):
    ...         self.distance_threshold = distance_threshold
    ...
    ...     def _l2_distance(self, c1, c2):
    ...         return math.sqrt(
    ...             (c1["x"] - c2["x"]) ** 2 + (c1["y"] - c2["y"]) ** 2
    ...         )
    ...     # you can also override match method
    ...     # def match(self, level):
    ...     #    return True
    ...
    ...     def diff(self, level, diff_instance):
    ...         l2_distance = self._l2_distance(level.t1, level.t2)
    ...         if l2_distance > self.distance_threshold:
    ...             diff_instance.custom_report_result('distance_too_far', level, {
    ...                 "l2_distance": l2_distance
    ...             })
    ...         #
    ...         return True
    ...
    >>> DeepDiff(t1, t2, custom_operators=[L2DistanceDifferWithPreventDefault(1)])
    {'distance_too_far':  {"root['coordinates'][0]": {'l2_distance': 1.4142135623730951},
                          "root['coordinates'][1]": {'l2_distance': 113.13708498984761}}}


Back to :doc:`/index`
