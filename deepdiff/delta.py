from copy import deepcopy
from ordered_set import OrderedSet
from deepdiff.helper import strings, numbers
from ast import literal_eval

GETATTR = 'GETATTR'
GET = 'GET'

VERIFICATION_MSG = ('Expected the previous value for {} to be {} but it is {}. '
                    'If you do not want this verification to happen, '
                    'initialize the delta object with verify_change=False.')


def _add_to_elements(elements, elem, inside):
    try:
        elem = literal_eval(elem)
    except ValueError:
        pass
    action = GETATTR if inside == '.' else GET
    elements.append((elem, action))


ALLOWED_BEGINNING_TO_ENDS = {
    '.': {'.', '['},
    '[': {']'},
}


class NotFound:

    def __eq__(self, other):
        return False

    __req__ = __eq__

    def __repr__(self):
        return 'not found'

    __str__ = __repr__


not_found = NotFound()


def _path_to_elements(path):
    """
    Given a path, it extracts the elements that form the path and their relevant most likely retrieval action.

        >>> from deepdiff import _path_to_elements
        >>> path = "root[4.3].b['a3']"
        >>> _path_to_elements(path)
        [(4.3, 'GET'), ('b', 'GETATTR'), ('a3', 'GET')]
    """
    elements = []
    elem = ''
    inside = False
    prev_char = None
    for char in path:
        if prev_char == '\\':
            elem += char
        if char == '[':
            if inside == '.':
                _add_to_elements(elements, elem, inside)
            inside = '['
            elem = ''
        elif char == '.':
            if inside == '[':
                elem += char
            elif inside == '.':
                _add_to_elements(elements, elem, inside)
                elem = ''
            else:
                inside = '.'
                elem = ''
        elif char == ']':
            _add_to_elements(elements, elem, inside)
            elem = ''
            inside = False
        else:
            elem += char
        prev_char = char
    if elem:
        _add_to_elements(elements, elem, inside)
    return elements


def _get_nested_obj(obj, elements):
    for (elem, action) in elements:
        if action == GET:
            obj = obj[elem]
        elif action == GETATTR:
            obj = getattr(obj, elem)
    return obj


class Delta:

    def __init__(self, diff, mutate=False, verify_change=True):
        self.diff = diff
        self.mutate = mutate
        self.verify_change = verify_change

    def __add__(self, other):
        if not self.mutate:
            other = deepcopy(other)
        self._do_values_changed(other)
        self._do_iterable_item_added(other)
        # NOTE: the remove iterable action needs to happen AFTER all the other iterables.
        self._do_iterable_item_removed(other)

        return other

    __radd__ = __add__

    def _do_verify_changes(self, path, expected_old_value, current_old_value):
        if self.verify_change and expected_old_value != current_old_value:
            raise ValueError(VERIFICATION_MSG.format(path, expected_old_value, current_old_value))

    def _get_index_or_key(self, obj, index, path, expected_old_value):
        try:
            current_old_value = obj[index]
        except (KeyError, IndexError):
            current_old_value = not_found
            if self.verify_change:
                raise ValueError(VERIFICATION_MSG.format(path, expected_old_value, current_old_value)) from None
            return not_found
        return current_old_value

    def _do_iterable_item_added(self, other):
        iterable_item_added = self.diff.get('iterable_item_added', {})
        for path, value in iterable_item_added.items():
            elements = _path_to_elements(path)
            obj = _get_nested_obj(obj=other, elements=elements[:-1])
            index = elements[-1][0]
            obj.insert(index, value)

    def _do_values_changed(self, other):
        values_changed = self.diff.get('values_changed', {})
        for path, value in values_changed.items():
            elements = _path_to_elements(path)
            obj = _get_nested_obj(obj=other, elements=elements[:-1])
            index = elements[-1][0]
            action = elements[-1][1]
            expected_old_value = value.get('old_value', not_found)
            if action == GET:
                current_old_value = obj[index]
                obj[index] = value['new_value']
            elif action == GETATTR:
                current_old_value = getattr(obj, index)
                setattr(obj, index, value['new_value'])
            self._do_verify_changes(path, expected_old_value, current_old_value)

    def _do_iterable_item_removed(self, other):
        iterable_item_removed = self.diff.get('iterable_item_removed', {})
        num = 0
        for path, expected_old_value in iterable_item_removed.items():
            elements = _path_to_elements(path)
            obj = _get_nested_obj(obj=other, elements=elements[:-1])
            index = elements[-1][0] - num
            current_old_value = self._get_index_or_key(obj, index, path, expected_old_value)
            if current_old_value is not_found:
                continue
            self._do_verify_changes(path, expected_old_value, current_old_value)
            del obj[index]
            num += 1


if __name__ == "__main__":  # pragma: no cover
    import doctest
    doctest.testmod()
