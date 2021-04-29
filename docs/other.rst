:doc:`/index`

Other Parameters
================

.. _iterable_compare_func_label:

Iterable Compare Func
---------------------

New in DeepDiff 5.5.0

There are times that we want to guide DeepDiff as to what items to compare with other items. In such cases we can pass a `iterable_compare_func` that takes a function pointer to compare two items. It function takes two parameters and should return `True` if it is a match, `False` if it is not a match or raise `CannotCompare` if it is unable to compare the two.


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





Back to :doc:`/index`
