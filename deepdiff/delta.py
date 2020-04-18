import logging
from collections.abc import Mapping
from copy import deepcopy
from decimal import Decimal
from deepdiff import DeepDiff
from deepdiff.serialization import pickle_load
from deepdiff.helper import py_current_version
from deepdiff.path import _path_to_elements, _get_nested_obj, GET, GETATTR

MINIMUM_PY_FOR_DELTA = Decimal('3.6')
DISABLE_DELTA = py_current_version < MINIMUM_PY_FOR_DELTA
DELTA_SKIP_MSG = 'Python {} or newer is needed for Delta.'.format(MINIMUM_PY_FOR_DELTA)


# TODO: it needs python3.6+ since dictionaries are ordered.

logger = logging.getLogger(__name__)


VERIFICATION_MSG = 'Expected the previous value for {} to be {} but it is {}.'
INDEX_NOT_FOUND_TO_ADD_MSG = 'Index of {} is not found for {} for insertion operation.'


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

    diff : A DeepDiff object or the path to a delta file or a loaded delta dictionary.

    **Returns**

        A delta object that can be added to t1 to recreate t2.

    **Examples**

    Importing
        >>> from deepdiff import DeepDiff, Delta
        >>> from pprint import pprint
    """
    def __init__(self, diff=None, mutate=False, verify_symmetry=False, raise_errors=False, log_errors=True):

        if isinstance(diff, DeepDiff):
            diff = diff.to_delta_dict()
        elif isinstance(diff, Mapping):
            pass

        self.diff = diff
        self.mutate = mutate
        self.verify_symmetry = verify_symmetry
        self.raise_errors = raise_errors
        self.log_errors = log_errors

    def __add__(self, other):
        if not self.mutate:
            other = deepcopy(other)
        self._do_values_changed(other)
        self._do_set_item_added(other)
        self._do_set_item_removed(other)
        self._do_iterable_item_added(other)
        # NOTE: the remove iterable action needs to happen AFTER all the other iterables.
        self._do_iterable_item_removed(other)

        return other

    __radd__ = __add__

    def load(self, file_path, safe_to_import=None):
        """
        **load**
        Read and load the delta object from a file_path

        **Parameters**

        file_path : Local path to the file to load

        safe_to_import : A set of modules that needs to be explicitly allowed to be loaded.
            Example: {'mymodule.MyClass', 'decimal.Decimal'}
            Note that this set will be added to the basic set of modules that are already allowed.
            The set of what is already allowed can be found in deepdiff.serialization.SAFE_TO_IMPORT
        """
        with open(file_path, 'rb'):
            content = file_path.read()

        self.diff = pickle_load(content, safe_to_import=safe_to_import)

    def loads(self, content, safe_to_import=None):
        """
        **loads**
        load the delta object from a bytes object.
        Note: It works to pass a string too but then internally it is converted to bytes.

        **Parameters**

        content : Content to be loaded

        safe_to_import : A set of modules that needs to be explicitly allowed to be loaded.
            Example: {'mymodule.MyClass', 'decimal.Decimal'}
            Note that this set will be added to the basic set of modules that are already allowed.
            The set of what is already allowed can be found in deepdiff.serialization.SAFE_TO_IMPORT
        """

        self.diff = pickle_load(content, safe_to_import=safe_to_import)

    def _raise_or_log(self, msg, level='error'):
        if self.log_errors:
            getattr(logger, level)(msg)
        if self.raise_errors:
            raise DeltaError(msg) from None

    def _do_verify_changes(self, path, expected_old_value, current_old_value):
        if self.verify_symmetry and expected_old_value != current_old_value:
            self._raise_or_log(VERIFICATION_MSG.format(path, expected_old_value, current_old_value))

    def _get_index_or_key(self, obj, path, expected_old_value, index=None, attr=None):
        try:
            if index is not None:
                current_old_value = obj[index]
            elif attr is not None:
                current_old_value = getattr(obj, attr)
            else:
                raise DeltaError('index or attr need to be set when calling _get_index_or_key')
        except (KeyError, IndexError, AttributeError):
            current_old_value = not_found
            if self.verify_symmetry:
                self._raise_or_log(VERIFICATION_MSG.format(path, expected_old_value, current_old_value))
        return current_old_value

    def _do_iterable_item_added(self, other):
        iterable_item_added = self.diff.get('iterable_item_added', {})
        for path, value in iterable_item_added.items():
            elements = _path_to_elements(path)
            obj = _get_nested_obj(obj=other, elements=elements[:-1])
            index = elements[-1][0]
            if index <= len(obj):
                obj.insert(index, value)
            else:
                self._raise_or_log(INDEX_NOT_FOUND_TO_ADD_MSG.format(index, path))

    def _do_values_changed(self, other):
        values_changed = self.diff.get('values_changed', {})
        for path, value in values_changed.items():
            elements = _path_to_elements(path)
            obj = _get_nested_obj(obj=other, elements=elements[:-1])
            action = elements[-1][1]
            expected_old_value = value.get('old_value', not_found)
            if action == GET:
                index = elements[-1][0]
                current_old_value = self._get_index_or_key(
                    obj=obj, index=index, path=path, expected_old_value=expected_old_value)
                if current_old_value is not_found:
                    continue
                obj[index] = value['new_value']
            elif action == GETATTR:
                attr = elements[-1][0]
                current_old_value = self._get_index_or_key(
                    obj=obj, attr=attr, path=path, expected_old_value=expected_old_value)
                setattr(obj, index, value['new_value'])
            self._do_verify_changes(path, expected_old_value, current_old_value)

    def _do_iterable_item_removed(self, other):
        iterable_item_removed = self.diff.get('iterable_item_removed', {})
        num = 0
        for path, expected_old_value in iterable_item_removed.items():
            elements = _path_to_elements(path)
            obj = _get_nested_obj(obj=other, elements=elements[:-1])
            index = elements[-1][0] - num
            current_old_value = self._get_index_or_key(
                obj=obj, index=index, path=path, expected_old_value=expected_old_value)
            if current_old_value is not_found:
                continue
            self._do_verify_changes(path, expected_old_value, current_old_value)
            del obj[index]
            num += 1

    def _do_set_item_added(self, other):
        items = self.diff.get('set_item_added')
        if items:
            self._do_set_item(other, items, action='add')

    def _do_set_item_removed(self, other):
        items = self.diff.get('set_item_removed')
        if items:
            self._do_set_item(other, items, action='remove')

    def _do_set_item(self, other, items, action):
        for path, value in items.items():
            elements = _path_to_elements(path)
            obj = _get_nested_obj(obj=other, elements=elements)
            is_frozen = isinstance(obj, frozenset)
            if is_frozen:
                obj = set(obj)
            getattr(obj, action)(value)


if __name__ == "__main__":  # pragma: no cover
    import doctest
    doctest.testmod()
