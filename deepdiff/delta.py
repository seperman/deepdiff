import logging
from collections.abc import Mapping
from copy import deepcopy
from deepdiff import DeepDiff
from deepdiff.serialization import pickle_load
from deepdiff.helper import (
    DICT_IS_SORTED, MINIMUM_PY_DICT_TYPE_SORTED, strings, short_repr, numbers, np_ndarray, not_found)
from deepdiff.path import _path_to_elements, _get_nested_obj, GET, GETATTR

DISABLE_DELTA = not DICT_IS_SORTED
DELTA_SKIP_MSG = 'Python {} or newer is needed for Delta.'.format(MINIMUM_PY_DICT_TYPE_SORTED)


# TODO: it needs python3.6+ since dictionaries are ordered.

logger = logging.getLogger(__name__)


VERIFICATION_MSG = 'Expected the previous value for {} to be {} but it is {}. Due to {}'
ELEM_NOT_FOUND_TO_ADD_MSG = 'Key or index of {} is not found for {} for setting operation.'
TYPE_CHANGE_FAIL_MSG = 'Unable to do the type change for {} from to type {} due to {}'
VERIFY_SYMMETRY_MSG = 'that the original objects that the delta is made from must be different than what the delta is applied to.'
FAIL_TO_REMOVE_ITEM_IGNORE_ORDER_MSG = 'Failed to remove index[{}] on {}. It was expected to be {} but got {}'
DELTA_NUMPY_OPERATOR_OVERRIDE_MSG = (
    'A numpy ndarray is most likely being added to a delta. '
    'Due to Numpy override the + operator, you can only do: delta + ndarray '
    'and NOT ndarray + delta')


class DeltaError(ValueError):
    """
    Delta specific errors
    """
    pass


class DeltaNumpyOperatorOverrideError(ValueError):
    """
    Delta Numpy Operator Override Error
    """
    pass


class Delta:
    r"""
    **Delta**

    DeepDiff Delta is a directed delta that when applied to t1 can yield t2 where delta is the difference of t1 and t2.

    NOTE: THIS FEATURE IS IN BETA

    **Parameters**

    diff : Delta dictionary, Delta dump payload or a DeepDiff object, default=None.
        Content to be loaded.

    delta_path : String, default=None.
        local path to the delta dump file to be loaded

    You need to pass either diff or delta_path but not both.

    safe_to_import : Set, default=None.
        A set of modules that needs to be explicitly white listed to be loaded
        Example: {'mymodule.MyClass', 'decimal.Decimal'}
        Note that this set will be added to the basic set of modules that are already white listed.
        The set of what is already white listed can be found in deepdiff.serialization.SAFE_TO_IMPORT

    mutate : Boolean, default=False.
        Whether to mutate the original object when adding the delta to it or not.
        Note that this parameter is not always successful in mutating. For example if your original object
        is an immutable type such as a frozenset or a tuple, mutation will not succeed.
        Hence it is recommended to keep this parameter as the default value of False unless you are sure
        that you do not have immutable objects. There is a small overhead of doing deepcopy on the original
        object when mutate=False. If performance is a concern and modifying the original object is not a big deal,
        set the mutate=True but always reassign the output back to the original object.

        Example:

        delta = Delta(diff, mutate=True)

    **Returns**

        A delta object that can be added to t1 to recreate t2.

    **Examples**

    Importing
        >>> from deepdiff import DeepDiff, Delta
        >>> from pprint import pprint
    """
    def __init__(self, diff=None, delta_path=None, mutate=False, verify_symmetry=False, raise_errors=False, log_errors=True, safe_to_import=None):

        if diff is not None:
            if isinstance(diff, DeepDiff):
                self.diff = diff.to_delta_dict()
            elif isinstance(diff, Mapping):
                self.diff = diff
            elif isinstance(diff, strings):
                self.diff = pickle_load(diff, safe_to_import=safe_to_import)
        elif delta_path:
            with open(delta_path, 'rb'):
                content = delta_path.read()
            self.diff = pickle_load(content, safe_to_import=safe_to_import)
        else:
            raise ValueError('Either diff or delta_path need to be specified.')

        self.mutate = mutate
        self.verify_symmetry = verify_symmetry
        self.raise_errors = raise_errors
        self.log_errors = log_errors
        self.numpy_used = self.diff.pop('numpy_used', False)
        self.reset()

    def __repr__(self):
        return "<Delta: {}>".format(short_repr(self.diff, max_length=100))

    def reset(self):
        self.post_process_paths_to_convert = {}

    def __add__(self, other):
        if isinstance(other, numbers) and self.numpy_used:
            raise DeltaNumpyOperatorOverrideError(DELTA_NUMPY_OPERATOR_OVERRIDE_MSG)
        if self.mutate:
            self.root = other
        else:
            self.root = deepcopy(other)
        self._do_values_changed()
        self._do_set_item_added()
        self._do_set_item_removed()
        self._do_type_changes()
        # NOTE: the remove iterable action needs to happen BEFORE
        # all the other iterables to match the reverse of order of operations in DeepDiff
        self._do_iterable_item_removed()
        self._do_iterable_item_added()
        self._do_ignore_order()
        self._do_dictionary_item_added()
        self._do_dictionary_item_removed()
        self._do_attribute_added()
        self._do_attribute_removed()
        self._do_post_process()

        other = self.root
        # removing the reference to other
        del self.root
        self.reset()
        return other

    __radd__ = __add__

    def _raise_or_log(self, msg, level='error'):
        if self.log_errors:
            getattr(logger, level)(msg)
        if self.raise_errors:
            raise DeltaError(msg) from None

    def _do_verify_changes(self, path, expected_old_value, current_old_value):
        if self.verify_symmetry and expected_old_value != current_old_value:
            self._raise_or_log(VERIFICATION_MSG.format(
                path, expected_old_value, current_old_value, VERIFY_SYMMETRY_MSG))

    def _get_elem_and_compare_to_old_value(self, obj, path_for_err_reporting, expected_old_value, elem=None, action=None):
        try:
            if action == GET:
                current_old_value = obj[elem]
            elif action == GETATTR:
                current_old_value = getattr(obj, elem)
            else:
                raise DeltaError('invalid action when calling _get_elem_and_compare_to_old_value')
        except (KeyError, IndexError, AttributeError) as e:
            current_old_value = not_found
            if self.verify_symmetry:
                if isinstance(path_for_err_reporting, (list, tuple)):
                    path_for_err_reporting = '.'.join([i[0] for i in path_for_err_reporting])
                self._raise_or_log(VERIFICATION_MSG.format(
                    path_for_err_reporting,
                    expected_old_value, current_old_value, e))
        return current_old_value

    def _simple_set_elem_value(self, obj, path_for_err_reporting, elem=None, value=None, action=None):
        """
        Set the element value directly on an object
        """
        try:
            if action == GET:
                try:
                    obj[elem] = value
                except IndexError:
                    if elem == len(obj):
                        obj.append(value)
                    else:
                        self._raise_or_log(ELEM_NOT_FOUND_TO_ADD_MSG.format(elem, path_for_err_reporting))
            elif action == GETATTR:
                setattr(obj, elem, value)
            else:
                raise DeltaError('invalid action when calling _simple_set_elem_value')
        except (KeyError, IndexError, AttributeError) as e:
            self._raise_or_log('Failed to set {} due to {}'.format(path_for_err_reporting, e))

    def _set_new_value(self, parent, parent_to_obj_elem, parent_to_obj_action,
                       obj, elements, path, elem, action, new_value):
        """
        Set the element value on an object and if necessary convert the object to the proper mutable type
        """
        obj_is_new = False
        if isinstance(obj, tuple):
            # convert this object back to a tuple later
            self.post_process_paths_to_convert[elements[:-1]] = {'old_type': list, 'new_type': tuple}
            obj = list(obj)
            obj_is_new = True
        self._simple_set_elem_value(obj=obj, path_for_err_reporting=path, elem=elem,
                                    value=new_value, action=action)
        if obj_is_new and parent:
            # Making sure that the object is re-instated inside the parent especially if it was immutable
            # and we had to turn it into a mutable one. In such cases the object has a new id.
            self._simple_set_elem_value(obj=parent, path_for_err_reporting=path, elem=parent_to_obj_elem,
                                        value=obj, action=parent_to_obj_action)

    def _simple_delete_elem(self, obj, path_for_err_reporting, elem=None, action=None):
        """
        Delete the element directly on an object
        """
        try:
            if action == GET:
                del obj[elem]
            elif action == GETATTR:
                del obj.__dict__[elem]
            else:
                raise DeltaError('invalid action when calling _simple_set_elem_value')
        except (KeyError, IndexError, AttributeError) as e:
            self._raise_or_log('Failed to set {} due to {}'.format(path_for_err_reporting, e))

    def _del_elem(self, parent, parent_to_obj_elem, parent_to_obj_action,
                  obj, elements, path, elem, action):
        """
        Delete the element value on an object and if necessary convert the object to the proper mutable type
        """
        obj_is_new = False
        if isinstance(obj, tuple):
            # convert this object back to a tuple later
            self.post_process_paths_to_convert[elements[:-1]] = {'old_type': list, 'new_type': tuple}
            obj = list(obj)
            obj_is_new = True
        self._simple_delete_elem(obj=obj, path_for_err_reporting=path, elem=elem, action=action)
        if obj_is_new and parent:
            # Making sure that the object is re-instated inside the parent especially if it was immutable
            # and we had to turn it into a mutable one. In such cases the object has a new id.
            self._simple_set_elem_value(obj=parent, path_for_err_reporting=path, elem=parent_to_obj_elem,
                                        value=obj, action=parent_to_obj_action)

    def _do_iterable_item_added(self):
        iterable_item_added = self.diff.get('iterable_item_added')
        if iterable_item_added:
            self._do_item_added(iterable_item_added)

    def _do_dictionary_item_added(self):
        dictionary_item_added = self.diff.get('dictionary_item_added')
        if dictionary_item_added:
            self._do_item_added(dictionary_item_added)

    def _do_attribute_added(self):
        attribute_added = self.diff.get('attribute_added')
        if attribute_added:
            self._do_item_added(attribute_added)

    def _do_item_added(self, items):
        for path, new_value in items.items():
            elements, parent, parent_to_obj_elem, parent_to_obj_action, obj, elem, action = self._get_elements_and_details(path)

            self._set_new_value(parent, parent_to_obj_elem, parent_to_obj_action,
                                obj, elements, path, elem, action, new_value)

    def _do_values_changed(self):
        values_changed = self.diff.get('values_changed')
        if values_changed:
            self._do_values_or_type_changed(values_changed)

    def _do_type_changes(self):
        type_changes = self.diff.get('type_changes')
        if type_changes:
            self._do_values_or_type_changed(type_changes, is_type_change=True)

    def _do_post_process(self):
        if self.post_process_paths_to_convert:
            self._do_values_or_type_changed(self.post_process_paths_to_convert, is_type_change=True)

    def _get_elements_and_details(self, path):
        elements = _path_to_elements(path)
        if len(elements) > 1:
            parent = _get_nested_obj(obj=self, elements=elements[:-2])
            parent_to_obj_elem, parent_to_obj_action = elements[-2]
            obj = self._get_elem_and_compare_to_old_value(
                obj=parent, path_for_err_reporting=path, expected_old_value=None,
                elem=parent_to_obj_elem, action=parent_to_obj_action)
        else:
            parent = parent_to_obj_elem = parent_to_obj_action = None
            obj = _get_nested_obj(obj=self, elements=elements[:-1])
        elem, action = elements[-1]
        return elements, parent, parent_to_obj_elem, parent_to_obj_action, obj, elem, action

    def _do_values_or_type_changed(self, changes, is_type_change=False):
        for path, value in changes.items():
            elements, parent, parent_to_obj_elem, parent_to_obj_action, obj, elem, action = self._get_elements_and_details(path)
            expected_old_value = value.get('old_value', not_found)

            current_old_value = self._get_elem_and_compare_to_old_value(
                obj=obj, path_for_err_reporting=path, expected_old_value=expected_old_value, elem=elem, action=action)
            if current_old_value is not_found:
                continue
            # With type change if we could have originally converted the type from old_value
            # to new_value just by applying the class of the new_value, then we might not include the new_value
            # in the delta dictionary.
            if is_type_change and 'new_value' not in value:
                try:
                    new_value = value['new_type'](current_old_value)
                except Exception as e:
                    self._raise_or_log(TYPE_CHANGE_FAIL_MSG.format(obj[elem], value.get('new_type', 'unknown'), e))
                    continue
            else:
                new_value = value['new_value']

            self._set_new_value(parent, parent_to_obj_elem, parent_to_obj_action,
                                obj, elements, path, elem, action, new_value)

            self._do_verify_changes(path, expected_old_value, current_old_value)

    def _do_item_removed(self, tuples):
        """
        Handle removing tuples.
        Note: tuples needs to be a list of tuples or tuple of tuples om the form of (key, value)
        """
        for path, expected_old_value in tuples:
            elements, parent, parent_to_obj_elem, parent_to_obj_action, obj, elem, action = self._get_elements_and_details(path)
            current_old_value = self._get_elem_and_compare_to_old_value(
                obj=obj, elem=elem, path_for_err_reporting=path, expected_old_value=expected_old_value, action=action)
            if current_old_value is not_found:
                continue
            self._del_elem(parent, parent_to_obj_elem, parent_to_obj_action,
                           obj, elements, path, elem, action)
            self._do_verify_changes(path, expected_old_value, current_old_value)

    def _do_iterable_item_removed(self):
        iterable_item_removed = self.diff.get('iterable_item_removed')
        # Sorting the iterable_item_removed in reverse order based on the paths.
        # So that we delete a bigger index before a smaller index
        if iterable_item_removed:
            iterable_item_removed = sorted(iterable_item_removed.items(), key=lambda x: x[0], reverse=True)
            self._do_item_removed(iterable_item_removed)

    def _do_dictionary_item_removed(self):
        dictionary_item_removed = self.diff.get('dictionary_item_removed')
        if dictionary_item_removed:
            self._do_item_removed(dictionary_item_removed.items())

    def _do_attribute_removed(self):
        attribute_removed = self.diff.get('attribute_removed')
        if attribute_removed:
            self._do_item_removed(attribute_removed.items())

    def _do_set_item_added(self):
        items = self.diff.get('set_item_added')
        if items:
            self._do_set_or_frozenset_item(items, func='union')

    def _do_set_item_removed(self):
        items = self.diff.get('set_item_removed')
        if items:
            self._do_set_or_frozenset_item(items, func='difference')

    def _do_set_or_frozenset_item(self, items, func):
        for path, value in items.items():
            elements = _path_to_elements(path)
            parent = _get_nested_obj(obj=self, elements=elements[:-1])
            elem, action = elements[-1]
            obj = self._get_elem_and_compare_to_old_value(
                parent, path_for_err_reporting=path, expected_old_value=None, elem=elem, action=action)
            new_value = getattr(obj, func)(value)
            self._simple_set_elem_value(parent, path_for_err_reporting=path, elem=elem, value=new_value, action=action)

    def _do_ignore_order_get_old(self, obj, remove_indexes_per_path, fixed_indexes_values, path_for_err_reporting):
        """
        A generator that gets the old values in an iterable when the order was supposed to be ignored.
        """
        old_obj_index = -1
        max_len = len(obj) - 1
        while old_obj_index < max_len:
            old_obj_index += 1
            current_old_obj = obj[old_obj_index]
            if current_old_obj in fixed_indexes_values:
                continue
            if old_obj_index in remove_indexes_per_path:
                expected_obj_to_delete = remove_indexes_per_path.pop(old_obj_index)
                if current_old_obj == expected_obj_to_delete:
                    continue
                else:
                    self._raise_or_log(FAIL_TO_REMOVE_ITEM_IGNORE_ORDER_MSG.format(old_obj_index, path_for_err_reporting, expected_obj_to_delete, current_old_obj))
            yield current_old_obj

    def _do_ignore_order(self):
        """

            't1': [5, 1, 1, 1, 6],
            't2': [7, 1, 1, 1, 8],

            'iterable_items_added_at_indexes': {
                'root': {
                    0: 7,
                    4: 8
                }
            },
            'iterable_items_removed_at_indexes': {
                'root': {
                    4: 6,
                    0: 5
                }
            }

        """
        fixed_indexes = self.diff.get('iterable_items_added_at_indexes', {})
        remove_indexes = self.diff.get('iterable_items_removed_at_indexes', {})
        # import pytest; pytest.set_trace()
        paths = set(fixed_indexes.keys()) | set(remove_indexes.keys())
        for path in paths:
            # In the case of ignore_order reports, we are pointing to the container object.
            # Thus we add a [0] to the elements so we can get the required objects and discard what we don't need.
            _, parent, parent_to_obj_elem, parent_to_obj_action, obj, _, _ = self._get_elements_and_details("{}[0]".format(path))
            # copying both these dictionaries since we don't want to mutate them.
            fixed_indexes_per_path = fixed_indexes.get(path, {}).copy()
            remove_indexes_per_path = remove_indexes.get(path, {}).copy()
            # TODO: this needs to be changed to use deephash so any item can be in this set even if not hashable.
            fixed_indexes_values = set(fixed_indexes_per_path.values())

            new_obj = []
            # Numpy's NdArray does not like the bool function.
            if isinstance(obj, np_ndarray):
                there_are_old_items = obj.size > 0
            else:
                there_are_old_items = bool(obj)
            old_item_gen = self._do_ignore_order_get_old(
                obj, remove_indexes_per_path, fixed_indexes_values, path_for_err_reporting=path)
            while there_are_old_items or fixed_indexes_per_path:
                new_obj_index = len(new_obj)
                if new_obj_index in fixed_indexes_per_path:
                    new_item = fixed_indexes_per_path.pop(new_obj_index)
                    new_obj.append(new_item)
                else:
                    try:
                        new_item = next(old_item_gen)
                    except StopIteration:
                        there_are_old_items = False
                    else:
                        new_obj.append(new_item)

            if isinstance(obj, tuple):
                new_obj = tuple(new_obj)
            # Making sure that the object is re-instated inside the parent especially if it was immutable
            # and we had to turn it into a mutable one. In such cases the object has a new id.
            self._simple_set_elem_value(obj=parent, path_for_err_reporting=path, elem=parent_to_obj_elem,
                                        value=new_obj, action=parent_to_obj_action)


if __name__ == "__main__":  # pragma: no cover
    import doctest
    doctest.testmod()
