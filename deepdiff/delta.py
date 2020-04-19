import logging
from collections.abc import Mapping
from copy import deepcopy
from decimal import Decimal
from deepdiff import DeepDiff
from deepdiff.serialization import pickle_load
from deepdiff.helper import py_current_version, strings
from deepdiff.path import _path_to_elements, _get_nested_obj, GET, GETATTR

MINIMUM_PY_FOR_DELTA = Decimal('3.6')
DISABLE_DELTA = py_current_version < MINIMUM_PY_FOR_DELTA
DELTA_SKIP_MSG = 'Python {} or newer is needed for Delta.'.format(MINIMUM_PY_FOR_DELTA)


# TODO: it needs python3.6+ since dictionaries are ordered.

logger = logging.getLogger(__name__)


VERIFICATION_MSG = 'Expected the previous value for {} to be {} but it is {}. Due to {}'
INDEX_NOT_FOUND_TO_ADD_MSG = 'Index of {} is not found for {} for insertion operation.'
TYPE_CHANGE_FAIL_MSG = 'Unable to do the type change for {} from to type {} due to {}'
VERIFY_SYMMETRY_MSG = 'that the original objects that the delta is made from must be different than what the delta is applied to.'


class _NotFound:

    def __eq__(self, other):
        return False

    __req__ = __eq__

    def __repr__(self):
        return 'not found'

    __str__ = __repr__


not_found = _NotFound()


class DeltaError(ValueError):
    """
    Delta specific errors
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

        if diff:
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

    def reset(self):
        self.post_process_paths_to_convert = {}

    def __add__(self, other):
        self.reset()
        if self.mutate:
            self.root = other
        else:
            self.root = deepcopy(other)
        self._do_values_changed()
        self._do_set_item_added()
        self._do_set_item_removed()
        self._do_type_changes()
        self._do_iterable_item_added()
        # NOTE: the remove iterable action needs to happen AFTER all the other iterables.
        self._do_iterable_item_removed()
        self._do_post_process()

        other = self.root
        # removing the reference to other
        del self.root
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

    def _get_old_value_index_or_key(self, obj, path_for_err_reporting, expected_old_value, index=None, action=None):
        try:
            if action == GET:
                current_old_value = obj[index]
            elif action == GETATTR:
                current_old_value = getattr(obj, index)
            else:
                raise DeltaError('invalid action when calling _get_old_value_index_or_key')
        except (KeyError, IndexError, AttributeError) as e:
            current_old_value = not_found
            if self.verify_symmetry:
                self._raise_or_log(VERIFICATION_MSG.format(
                    path_for_err_reporting,
                    expected_old_value, current_old_value, e))
        return current_old_value

    def _set_old_index_or_key(self, obj, path_for_err_reporting, index=None, value=None, action=None):
        try:
            if action == GET:
                obj[index] = value
            elif action == GETATTR:
                setattr(obj, index, value)
            else:
                raise DeltaError('invalid action when calling _set_old_index_or_key')
        except (KeyError, IndexError, AttributeError) as e:
            self._raise_or_log('Failed to set {} due to {}'.format(path_for_err_reporting, e))
        return obj

    def _do_iterable_item_added(self):
        iterable_item_added = self.diff.get('iterable_item_added', {})
        for path, value in iterable_item_added.items():
            elements = _path_to_elements(path)
            obj = _get_nested_obj(obj=self, elements=elements[:-1])
            index = elements[-1][0]
            if index <= len(obj):
                obj.insert(index, value)
            else:
                self._raise_or_log(INDEX_NOT_FOUND_TO_ADD_MSG.format(index, path))

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

    def _do_values_or_type_changed(self, changes, is_type_change=False):
        for path, value in changes.items():
            elements = _path_to_elements(path)
            if len(elements) > 1:
                parent = _get_nested_obj(obj=self, elements=elements[:-2])
                parent_to_obj_elem, parent_to_obj_action = elements[-2]
                obj = self._get_old_value_index_or_key(
                    obj=parent, path_for_err_reporting=path, expected_old_value=None,
                    index=parent_to_obj_elem, action=parent_to_obj_action)
            else:
                parent = None
                obj = _get_nested_obj(obj=self, elements=elements[:-1])
            index, action = elements[-1]
            expected_old_value = value.get('old_value', not_found)

            current_old_value = self._get_old_value_index_or_key(
                obj=obj, path_for_err_reporting=path, expected_old_value=expected_old_value, index=index, action=action)
            if current_old_value is not_found:
                continue
            # With type change if we could have originally converted the type from old_value
            # to new_value just by applying the class of the new_value, then we might not include the new_value
            # in the delta dictionary.
            if is_type_change and 'new_value' not in value:
                try:
                    new_value = value['new_type'](current_old_value)
                except Exception as e:
                    self._raise_or_log(TYPE_CHANGE_FAIL_MSG.format(obj[index], value.get('new_type', 'unknown'), e))
                    continue
            else:
                new_value = value['new_value']

            if isinstance(obj, tuple):
                # convert this object back to a tuple later
                self.post_process_paths_to_convert[elements[:-1]] = {'old_type': list, 'new_type': tuple}
                obj = list(obj)
            obj = self._set_old_index_or_key(obj=obj, path_for_err_reporting=path, index=index,
                                             value=new_value, action=action)
            if parent:
                self._set_old_index_or_key(obj=parent, path_for_err_reporting=path, index=parent_to_obj_elem,
                                           value=obj, action=parent_to_obj_action)
            self._do_verify_changes(path, expected_old_value, current_old_value)

    def _do_iterable_item_removed(self):
        iterable_item_removed = self.diff.get('iterable_item_removed', {})
        num = 0
        for path, expected_old_value in iterable_item_removed.items():
            elements = _path_to_elements(path)
            obj = _get_nested_obj(obj=self, elements=elements[:-1])
            index, action = elements[-1]
            index -= num
            current_old_value = self._get_old_value_index_or_key(
                obj=obj, index=index, path_for_err_reporting=path, expected_old_value=expected_old_value, action=action)
            if current_old_value is not_found:
                continue
            self._do_verify_changes(path, expected_old_value, current_old_value)
            del obj[index]
            num += 1

    def _do_set_item_added(self):
        items = self.diff.get('set_item_added')
        if items:
            self._do_set_item(items, func='union')

    def _do_set_item_removed(self):
        items = self.diff.get('set_item_removed')
        if items:
            self._do_set_item(items, func='difference')

    def _do_set_item(self, items, func):
        for path, value in items.items():
            elements = _path_to_elements(path)
            parent = _get_nested_obj(obj=self, elements=elements[:-1])
            elem, action = elements[-1]
            obj = self._get_old_value_index_or_key(parent, path_for_err_reporting=path, expected_old_value=None, index=elem, action=action)
            new_value = getattr(obj, func)(value)
            self._set_old_index_or_key(parent, path_for_err_reporting=path, index=elem, value=new_value, action=action)


if __name__ == "__main__":  # pragma: no cover
    import doctest
    doctest.testmod()
