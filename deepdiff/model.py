# -*- coding: utf-8 -*-

from .helper import items
from .helper import is_string
from .helper import RemapDict
from abc import ABCMeta, abstractmethod
from ast import literal_eval
from copy import copy


class ResultDict(RemapDict):
    def cleanup(self):
        """
        Remove empty keys from this object. Should always be called after the result is final.
        :return:
        """
        empty_keys = [k for k, v in getattr(self, items)() if not v]

        for k in empty_keys:
            del self[k]


class RefStyleResultDict(ResultDict):
    def __init__(self):
        # TODO: centralize keys
        self.update({"type_changes": set(),
                     "dictionary_item_added": set(), "dictionary_item_removed": set(),
                     "values_changed": set(), "unprocessed": set(),
                     "iterable_item_added": set(), "iterable_item_removed": set(),
                     "attribute_added": set(), "attribute_removed": set(),
                     "set_item_removed": set(), "set_item_added": set(),
                     "repetition_change": set()})


class TextStyleResultDict(ResultDict):
    def __init__(self, verbose_level = 1, ref_results = None):
        self.verbose_level = verbose_level

        # TODO: centralize keys
        self.update({"type_changes": {}, "dictionary_item_added": self.__set_or_dict(),
                     "dictionary_item_removed": self.__set_or_dict(),
                     "values_changed": {}, "unprocessed": [], "iterable_item_added": {}, "iterable_item_removed": {},
                     "attribute_added": self.__set_or_dict(), "attribute_removed": self.__set_or_dict(),
                     "set_item_removed": set([]),
                     "set_item_added": set([]), "repetition_change": {}})

        if ref_results:
            self.from_ref_results(ref_results)

    def __set_or_dict(self):
        return {} if self.verbose_level >= 2 else set()
        #return dict()

    def from_ref_results(self, ref):
        """
        Populate this object by parsing an existing reference-style result dictionary.
        :param ref: A RefStyleResultDict
        :return:
        """
        self._from_ref_type_changes(ref)
        self._from_ref_default(ref, 'dictionary_item_added')
        self._from_ref_default(ref, 'dictionary_item_removed')
        self._from_ref_value_changed(ref)
        self._from_ref_unprocessed(ref)
        self._from_ref_default(ref, 'iterable_item_added')
        self._from_ref_default(ref, 'iterable_item_removed')
        self._from_ref_default(ref, 'attribute_added')
        self._from_ref_default(ref, 'attribute_removed')
        self._from_ref_set_item_removed(ref)
        self._from_ref_set_item_added(ref)
        self._from_ref_repetition_change(ref)

    def _from_ref_default(self, ref, report_type):
        if report_type in ref:
            for change in ref[report_type]:  # report each change
                # determine change direction (added or removed)
                # Report t2 (the new one) whenever possible.
                # In cases where t2 doesn't exist (i.e. stuff removed), report t1.
                if change.t2 is not None:
                    item = change.t2
                else:
                    item = change.t1

                # do the reporting
                if isinstance(self[report_type], set):
                    self[report_type].add(change.path(force='fake'))
                elif isinstance(self[report_type], dict):
                    self[report_type][change.path(force='fake')] = item
                elif isinstance(self[report_type], list):    # pragma: no cover
                    # we don't actually have any of those right now, but just in case
                    self[report_type].append(change.path(force='fake'))
                else:                                        # pragma: no cover
                    # should never happen
                    raise TypeError("Cannot handle this report container type.")

    def _from_ref_type_changes(self, ref):
        if 'type_changes' in ref:
            for change in ref['type_changes']:
                self['type_changes'][change.path(force='fake')] = RemapDict({'old_type': type(change.t1), 'new_type': type(change.t2)})
                if self.verbose_level:
                    self["type_changes"][change.path(force='fake')].update(old_value=change.t1, new_value=change.t2)

    def _from_ref_value_changed(self, ref):
        if 'values_changed' in ref:
            for change in ref['values_changed']:
                self['values_changed'][change.path(force='fake')] = {'new_value': change.t2, 'old_value': change.t1}
                if 'diff' in change.additional:
                    self['values_changed'][change.path(force='fake')].update({'diff': change.additional['diff']})

    def _from_ref_unprocessed(self, ref):
        if 'unprocessed' in ref:
            for change in ref['unprocessed']:
                self['unprocessed'].append("%s: %s and %s" % (change.path(force='fake'), change.t1, change.t2))

    def _from_ref_set_item_removed(self, ref):
        if 'set_item_removed' in ref:
            for change in ref['set_item_removed']:
                path = change.up.path()  # we want't the set's path, the removed item is not directly accessible
                item = change.t1
                if is_string(item):
                    item = "'%s'" % item
                self['set_item_removed'].add("%s[%s]" % (path, str(item)))
                # this syntax is rather peculiar, but it's DeepDiff 2.x compatible

    def _from_ref_set_item_added(self, ref):
        if 'set_item_added' in ref:
            for change in ref['set_item_added']:
                path = change.up.path()  # we want't the set's path, the added item is not directly accessible
                item = change.t2
                if is_string(item):
                    item = "'%s'" % item
                self['set_item_added'].add("%s[%s]" % (path, str(item)))
                # this syntax is rather peculiar, but it's DeepDiff 2.x compatible)

    def _from_ref_repetition_change(self, ref):
        if 'repetition_change' in ref:
            for change in ref['repetition_change']:
                path = change.path(force='fake')
                self['repetition_change'][path] = RemapDict(change.additional['rep'])
                self['repetition_change'][path]['value'] = change.t1


class DiffLevel():
    """
    An object of this class represents a single object-tree-level in a reported change.
    A double-linked list of these object describes a single change on all of it's levels.
    Looking at the tree of all changes, a list of those objects represents a single path through the tree
    (which is just fancy for "a change").
    This is the result object class for object reference style reports.
    """
    def __init__(self, t1, t2, down=None, up=None, report_type=None, child_rel1=None, child_rel2=None, additional=None):
        """
        :param child_rel1: Either:
                            - An existing ChildRelationship object describing the "down" relationship for t1; or
                            - A ChildRelationship subclass. In this case, we will create the ChildRelationship objects
                              for both t1 and t2.
                            Alternatives for child_rel1 and child_rel2 must be used consistently.
        :param child_rel2: Either:
                            - An existing ChildRelationship object describing the "down" relationship for t2; or
                            - The param argument for a ChildRelationship class we shall create.
                           Alternatives for child_rel1 and child_rel2 must be used consistently.
        """
        self.t1 = t1
        """The current-level object in the left hand tree"""

        self.t2 = t2
        """The current-level object in the right hand tree"""

        self.down = down
        """Another DiffLevel object describing this change one level deeper down the object tree"""

        self.up = up
        """Another DiffLevel object describing this change one level further up the object tree"""

        self.report_type = report_type
        """
        If this object is this change's deepest level, this contains a string describing the type of change.
        Examples: "set_item_added", "values_changed"
        """

        # Note: don't use {} as additional's default value - this would turn out to be always the same dict object
        if additional is not None:
            self.additional = additional
        else:
            self.additional = {}
        """
        For some types of changes we store some additional information.
        This is a dict containing this information.
        Currently, this is used for:
        - values_changed: In case the changes data is a multi-line string,
                          we include a textual diff as additional['diff'].
        - repetition_change: additional['rep']:
                             e.g. {'old_repeat': 2, 'new_repeat': 1, 'old_indexes': [0, 2], 'new_indexes': [2]}
        """

        if isinstance(child_rel1, type):  # we shall create ChildRelationship objects for t1 and t2
            self.auto_generate_child_rel(klass = child_rel1, param = child_rel2)
        else:                             # the user supplied ChildRelationship objects for t1 and t2
            self.t1_child_rel = child_rel1
            """
            A ChildRelationship object describing the relationship between t1 and it's child object,
            where t1's child object equals down.t1.
            If this relationship is representable as a string, str(self.t1_child_rel) returns a partial parsable python string,
            e.g. "[2]", ".my_attribute"
            """

            self.t2_child_rel = child_rel2
            """
            Another ChildRelationship object describing the relationship between t2 and it's child object.
            """

        self._path = None
        """Will cache result of .path() for performance"""

    def auto_generate_child_rel(self, klass, param):
        """
        Auto-populate self.child_rel1 and self.child_rel2.
        This requires self.down to be another valid DiffLevel object.
        :param klass: A ChildRelationship subclass describing the kind of parent-child relationship,
                      e.g. DictRelationship.
        :param param: A ChildRelationship subclass-dependent parameter describing how to get from parent to child,
                      e.g. the key in a dict
        """
        if self.down.t1:
            self.t1_child_rel = ChildRelationship.create(klass, self.t1, self.down.t1, param)
        if self.down.t2:
            self.t2_child_rel = ChildRelationship.create(klass, self.t2, self.down.t2, param)

    def all_up(self):
        """
        Get the root object of this comparison.
        (This is a convenient wrapper for following the up attribute as often as you can.)
        :rtype: DiffLevel
        """
        level = self
        while level.up:
            level = level.up
        return level

    def all_down(self):
        """
        Get the leaf object of this comparison.
        (This is a convenient wrapper for following the down attribute as often as you can.)
        :rtype: DiffLevel
        """
        level = self
        while level.down:
            level = level.down
        return level

    def path(self, root="root", force=None):
        """
        A python syntax string describing how to descend to this level, assuming the top level object is called root.
        Returns None if the path is not representable as a string.
        This might be the case for example if there are sets involved (because then there's not path at all) or because
        custom objects used as dictionary keys (then there is a path but it's not representable).
        Example: root['ingredients'][0]
        Note: We will follow the left side of the comparison branch, i.e. using the t1's to build the path.
        Using t1 or t2 should make no difference at all, except for the last step of a child-added/removed relationship.
        If it does in any other case, your comparison path is corrupt.
        :param root: The result string shall start with this var name
        :param force: Bends the meaning of "no string representation".
                      If None:
                        Will strictly return Python-parsable expressions. The result those yield will compare
                        equal to the objects in question.
                      If 'yes':
                        Will return a path including '(unrepresentable)' in place of non string-representable parts.
                      If 'fake':
                        Will try to produce an output optimized for readability.
                        This will pretend all iterables are subscriptable, for example.
        """
        # TODO: We could optimize this by building on top of self.up's path if it is cached there
        if self._path is not None:
            return self._path

        result = root
        level = self.all_up()  # start at the root

        # traverse all levels of this relationship
        while True:
            # get this level's relationship object
            if level == self:  # don't descend from self (or the path returned will be too deep)
                break
            else:
                next_rel = level.t1_child_rel or level.t2_child_rel  # next relationship object to get a partial from

            if next_rel is None:
                break

            # Build path for this level
            append = next_rel.access_partial(force)
            if append:
                result += append
            else:
                return None  # it seems this path is not representable as a string

            # Prepare processing next level
            if level.down is None:
                break
            else:
                level = level.down

        self._path = result
        return result

    def create_deeper(self, new_t1, new_t2, child_relationship_class, child_relationship_param=None, report_type=None):
        """
        Start a new comparison level and correctly link it to this one.
        :rtype: DiffLevel
        :return: New level
        """
        level = self.all_down()
        result = DiffLevel(new_t1, new_t2, down=None, up=level, report_type=report_type)
        level.down = result
        level.auto_generate_child_rel(child_relationship_class, child_relationship_param)
        return result

    def branch_deeper(self, new_t1, new_t2, child_relationship_class, child_relationship_param=None, report_type=None):
        """
        Branch this comparison: Do not touch this comparison line, but create a new one with exactly the same content,
        just one level deeper.
        :rtype: DiffLevel
        :return: New level in new comparison line
        """
        branch = self.copy()
        return branch.create_deeper(new_t1, new_t2, child_relationship_class, child_relationship_param, report_type)

    def copy(self):
        """
        Get a deep copy of this comparision line.
        :return: The leaf ("downmost") object of the copy.
        """
        orig = self.all_up()
        result = copy(orig)           # copy top level

        while orig is not None:
            result.additional = copy(orig.additional)

            if orig.down is not None:  # copy and create references to the following level
                # copy following level
                result.down = copy(orig.down)
                result.down.up = result        # adjust reverse link

                if orig.t1_child_rel is not None:
                    result.t1_child_rel = ChildRelationship.create(orig.t1_child_rel.__class__,
                                                                   result.t1, result.down.t1,
                                                                   orig.t1_child_rel.param)
                if orig.t2_child_rel is not None:
                    result.t2_child_rel = ChildRelationship.create(orig.t2_child_rel.__class__,
                                                                   result.t2, result.down.t2,
                                                                   orig.t2_child_rel.param)

            # descend to next level
            orig = orig.down
            if result.down is not None:
                result = result.down
        return result


class ChildRelationship():
    """
    Abstract Base class. Describes the relationship between a container object (the "parent") and the contained
    "child" object.
    """
    __metaclass__ = ABCMeta

    @staticmethod
    def create(klass, parent, child, param=None):
        if not issubclass(klass, ChildRelationship):
            raise TypeError
        return klass(parent, child, param)

    def __init__(self, parent, child, param=None):
        self.parent = parent
        """
        The parent object of this relationship, e.g. a dict
        """

        self.child = child
        """
        The child object of this relationship, e.g. a value in a dict
        """

        self.param = param
        """
        A subclass-dependent parameter describing how to get from parent to child, e.g. the key in a dict
        """

    def access_partial(self, force=None):
        """
        Returns a partial python parsable string describing this relationship,
        or None if the relationship is not representable as a string.
        This string can be appended to the parent Name.
        Subclasses representing a relationship that cannot be expressed as a string override this method to return None.
        Examples: "[2]", ".attribute", "['mykey']"
        :param force: Bends the meaning of "no string representation".
              If None:
                Will strictly return partials of Python-parsable expressions. The result those yield will compare
                equal to the objects in question.
              If 'yes':
                Will return a partial including '(unrepresentable)' instead of the non string-representable part.

        """
        stringified = self._param_to_str(force)
        if stringified:
            return self._format_partial(stringified)

    def access_string(self, parentname):
        """Combines a given parent var name with this relationships's access partial."""
        partial = self.access_partial()
        if partial:
            return parentname + partial
        else:
            return None

    @abstractmethod
    def _format_partial(self, partial):  # pragma: no cover
        """
        Formats an access partial to create a valid partial python string representing this relationship.
        E.g. for a dict, this turns a partial param "42" into "[42]".
        """
        pass

    def _param_to_str(self, force=None):
        """
        Convert param to a string. Return None if there is no string representation.
        This is called by access_partial()
        :param force: Bends the meaning of "no string representation".
                      If None:
                        Will strictly return Python-parsable expressions. The result those yield will compare
                        equal to the objects in question.
                      If 'yes':
                        Will return '(unrepresentable)' instead of None if there is no string representation
        """
        param = self.param
        if is_string(param):
            return self._format_param_str(param)
        else:
            candidate = str(param)
            try:
                resurrected = literal_eval(candidate)
                # Note: This will miss string-representable custom objects.
                # However, the only alternative I can currently think of is using eval() which is inherently dangerous.
            except (SyntaxError, ValueError):
                return self.__param_unparsable(param, force)
            if resurrected == param:
                return candidate
            else:
                return self.__param_unparsable(param, force)

    def _format_param_str(self, string):
        """
        This is a hook allowing subclasses to manipulate param strings.
        :param string: Input string
        :return: Manipulated string, as appropriate in this context.
        """
        return string

    @staticmethod
    def __param_unparsable(param, force=None):
        """Partial called by _param_to_str()"""
        if force == 'yes':
            return '(unrepresentable)'
        else:
            return None


class DictRelationship(ChildRelationship):
    def _format_partial(self, partial):
        return "[%s]" % partial

    def _format_param_str(self, string):
        """Overriding this b/c strings as dict keys must come in quotes."""
        return "'%s'" % string


class SubscriptableIterableRelationship(DictRelationship):
    pass  # for our purposes, we can see lists etc. as special cases of dicts


class InaccessibleRelationship(ChildRelationship):
    def _format_partial(self, partial):
        return None

    def access_partial(self, force=None):
        if force=='yes':
            return "(unrepresentable)"
        else:
            return None


class SetRelationship(InaccessibleRelationship):  # there is no random access to set elements
    pass


class NonSubscriptableIterableRelationship(InaccessibleRelationship):
    def access_partial(self, force=None):
        if force=='yes':
            return "(unrepresentable)"
        elif force=='fake' and self.param:
            stringified = self._param_to_str()
            if stringified:
                return "[%s]" % stringified
        elif force=='fake':
            return "[(unrepresentable)]"
        else:
            return None


class AttributeRelationship(ChildRelationship):
    def _format_partial(self, partial):
        return ".%s" % partial
