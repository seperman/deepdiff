import logging
from ast import literal_eval

# TODO: it needs python3.6+ since dictionaries are ordered.

logger = logging.getLogger(__name__)

GETATTR = 'GETATTR'
GET = 'GET'


class PathExtractionError(ValueError):
    pass


class RootCanNotBeModified(ValueError):
    pass


def _add_to_elements(elements, elem, inside):
    # Ignore private items
    if not elem.startswith('__'):
        try:
            elem = literal_eval(elem)
        except (ValueError, SyntaxError):
            pass
        action = GETATTR if inside == '.' else GET
        elements.append((elem, action))


DEFAULT_FIRST_ELEMENT = ('root', GETATTR)


def _path_to_elements(path, first_element=DEFAULT_FIRST_ELEMENT):
    """
    Given a path, it extracts the elements that form the path and their relevant most likely retrieval action.

        >>> from deepdiff import _path_to_elements
        >>> path = "root[4.3].b['a3']"
        >>> _path_to_elements(path, first_element=None)
        [(4.3, 'GET'), ('b', 'GETATTR'), ('a3', 'GET')]
    """
    elements = []
    if first_element:
        elements.append(first_element)
    elem = ''
    inside = False
    prev_char = None
    path = path[4:]  # removing "root from the beginning"
    for char in path:
        if prev_char == '\\':
            elem += char
        elif char == '[':
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
