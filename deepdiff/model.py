# -*- coding: utf-8 -*-

from deepdiff.helper import items, RemapDict, strings, short_repr, Verbose
from abc import ABCMeta, abstractmethod
from ast import literal_eval
from copy import copy

FORCE_DEFAULT = 'fake'


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
    def __init__(self, ref_results=None):

        # TODO: centralize keys
        self.update({"type_changes": {}, "dictionary_item_added": self.__set_or_dict(),
                     "dictionary_item_removed": self.__set_or_dict(),
                     "values_changed": {}, "unprocessed": [], "iterable_item_added": {}, "iterable_item_removed": {},
                     "attribute_added": self.__set_or_dict(), "attribute_removed": self.__set_or_dict(),
                     "set_item_removed": set(),
                     "set_item_added": set(), "repetition_change": {}})

        if ref_results:
            self.from_ref_results(ref_results)

    def __set_or_dict(self):
        return {} if Verbose.level >= 2 else set()

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
                report = self[report_type]
                if isinstance(report, set):
                    report.add(change.path(force=FORCE_DEFAULT))
                elif isinstance(report, dict):
                    report[change.path(force=FORCE_DEFAULT)] = item
                elif isinstance(report, list):    # pragma: no cover
                    # we don't actually have any of those right now, but just in case
                    report.append(change.path(force=FORCE_DEFAULT))
                else:  # pragma: no cover
                    # should never happen
                    raise TypeError("Cannot handle {} report container type.".format(report))

    def _from_ref_type_changes(self, ref):
        if 'type_changes' in ref:
            for change in ref['type_changes']:
                remap_dict = RemapDict({'old_type': type(change.t1),
                                        'new_type': type(change.t2)})
                self['type_changes'][change.path(force=FORCE_DEFAULT)] = remap_dict
                if Verbose.level:
                    remap_dict.update(old_value=change.t1, new_value=change.t2)

    def _from_ref_value_changed(self, ref):
        if 'values_changed' in ref:
            for change in ref['values_changed']:
                the_changed = {'new_value': change.t2, 'old_value': change.t1}
                self['values_changed'][change.path(force=FORCE_DEFAULT)] = the_changed
                if 'diff' in change.additional:
                    the_changed.update({'diff': change.additional['diff']})

    def _from_ref_unprocessed(self, ref):
        if 'unprocessed' in ref:
            for change in ref['unprocessed']:
                self['unprocessed'].append("%s: %s and %s" % (change.path(force=FORCE_DEFAULT), change.t1, change.t2))

    def _from_ref_set_item_removed(self, ref):
        if 'set_item_removed' in ref:
            for change in ref['set_item_removed']:
                path = change.up.path()  # we want't the set's path, the removed item is not directly accessible
                item = change.t1
                if isinstance(item, strings):
                    item = "'%s'" % item
                self['set_item_removed'].add("%s[%s]" % (path, str(item)))
                # this syntax is rather peculiar, but it's DeepDiff 2.x compatible

    def _from_ref_set_item_added(self, ref):
        if 'set_item_added' in ref:
            for change in ref['set_item_added']:
                path = change.up.path()  # we want't the set's path, the added item is not directly accessible
                item = change.t2
                if isinstance(item, strings):
                    item = "'%s'" % item
                self['set_item_added'].add("%s[%s]" % (path, str(item)))
                # this syntax is rather peculiar, but it's DeepDiff 2.x compatible)

    def _from_ref_repetition_change(self, ref):
        if 'repetition_change' in ref:
            for change in ref['repetition_change']:
                path = change.path(force=FORCE_DEFAULT)
                self['repetition_change'][path] = RemapDict(change.additional['rep'])
                self['repetition_change'][path]['value'] = change.t1


class DiffLevel(object):

    """
    An object of this class represents a single object-tree-level in a reported change.
    A double-linked list of these object describes a single change on all of its levels.
    Looking at the tree of all changes, a list of those objects represents a single path through the tree
    (which is just fancy for "a change").
    This is the result object class for object reference style reports.

    Example:

    >>> t1 = {2: 2, 4: 44}
    >>> t2 = {2: "b", 5: 55}
    >>> ddiff = DeepDiff(t1, t2, default_view='ref')
    >>> ddiff
    {'dictionary_item_added': {<DiffLevel id:4560126096, t1:None, t2:55>},
     'dictionary_item_removed': {<DiffLevel id:4560126416, t1:44, t2:None>},
     'type_changes': {<DiffLevel id:4560126608, t1:2, t2:b>}}

    Graph:

    <DiffLevel id:123, original t1,t2>          <DiffLevel id:200, original t1,t2>
                    ↑up                                         ↑up
                    |                                           |
                    | ChildRelationship                         | ChildRelationship
                    |                                           |
                    ↓down                                       ↓down
    <DiffLevel id:13, t1:None, t2:55>            <DiffLevel id:421, t1:44, t2:None>
    .path() = 'root[5]'                         .path() = 'root[4]'

    Note that the 2 top level DiffLevel objects are 2 different objects even though
    they are essentially talking about the same diff operation.


    A ChildRelationship object describing the relationship between t1 and it's child object,
    where t1's child object equals down.t1.

    Think about it like a graph:

    +---------------------------------------------------------------+
    |                                                               |
    |    parent                 difflevel                 parent    |
    |      +                          ^                     +       |
    +------|--------------------------|---------------------|-------+
           |                      |   | up                  |
           | Child                |   |                     | ChildRelationship
           | Relationship         |   |                     |
           |                 down |   |                     |
    +------|----------------------|-------------------------|-------+
    |      v                      v                         v       |
    |    child                  difflevel                 child     |
    |                                                               |
    +---------------------------------------------------------------+


    The child_rel example:

    # dictionary_item_removed is a set so in order to get an item from it:
    >>> difflevel = iter(ddiff['dictionary_item_removed']).next()
    >>> difflevel.up.t1_child_rel
    <DictRelationship id:456, parent:{2: 2, 4: 44}, child:44, param:4>

    >>> difflevel = iter(ddiff['dictionary_item_added']).next()
    >>> difflevel
    <DiffLevel id:4560126096, t1:None, t2:55>

    >>> difflevel.up
    >>> <DiffLevel id:4560154512, t1:{2: 2, 4: 44}, t2:{2: 'b', 5: 55}>

    >>> difflevel.up
    <DiffLevel id:4560154512, t1:{2: 2, 4: 44}, t2:{2: 'b', 5: 55}>

    # t1 didn't exist
    >>> difflevel.up.t1_child_rel

    # t2 is added
    >>> difflevel.up.t2_child_rel
    <DictRelationship id:4560154384, parent:{2: 'b', 5: 55}, child:55, param:5>

    """
    def __init__(self, t1, t2, down=None, up=None, report_type=None,
                 child_rel1=None, child_rel2=None, additional=None, verbose_level=1):
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

        # The current-level object in the left hand tree
        self.t1 = t1

        # The current-level object in the right hand tree
        self.t2 = t2

        # Another DiffLevel object describing this change one level deeper down the object tree
        self.down = down

        # Another DiffLevel object describing this change one level further up the object tree
        self.up = up

        self.report_type = report_type

        # If this object is this change's deepest level, this contains a string describing the type of change.
        # Examples: "set_item_added", "values_changed"

        # Note: don't use {} as additional's default value - this would turn out to be always the same dict object
        self.additional = {} if additional is None else additional

        # For some types of changes we store some additional information.
        # This is a dict containing this information.
        # Currently, this is used for:
        # - values_changed: In case the changes data is a multi-line string,
        #                   we include a textual diff as additional['diff'].
        # - repetition_change: additional['rep']:
        #                      e.g. {'old_repeat': 2, 'new_repeat': 1, 'old_indexes': [0, 2], 'new_indexes': [2]}
        # the user supplied ChildRelationship objects for t1 and t2

        # A ChildRelationship object describing the relationship between t1 and it's child object,
        # where t1's child object equals down.t1.
        # If this relationship is representable as a string, str(self.t1_child_rel) returns a partial parsable python string,
        # e.g. "[2]", ".my_attribute"
        self.t1_child_rel = child_rel1

        # Another ChildRelationship object describing the relationship between t2 and it's child object.
        self.t2_child_rel = child_rel2

        # Will cache result of .path() for performance
        self._path = None

    def __repr__(self):
        if Verbose.level == 0:
            result = "<{}>".format(self.path())
        elif Verbose.level >= 1:
            t1_repr = short_repr(self.t1)
            t2_repr = short_repr(self.t2)
            result = "<{} t1:{}, t2:{}>".format(self.path(), t1_repr, t2_repr)
        return result

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
            self.t1_child_rel = ChildRelationship.create(klass=klass, parent=self.t1,
                                                         child=self.down.t1, param=param)
        if self.down.t2:
            self.t2_child_rel = ChildRelationship.create(klass=klass, parent=self.t2,
                                                         child=self.down.t2, param=param)

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
            append = next_rel.get_partial(force)
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

    def create_deeper(self, new_t1, new_t2, child_relationship_class,
                      child_relationship_param=None, report_type=None):
        """
        Start a new comparison level and correctly link it to this one.
        :rtype: DiffLevel
        :return: New level
        """
        level = self.all_down()
        result = DiffLevel(new_t1, new_t2, down=None, up=level, report_type=report_type)
        level.down = result
        level.auto_generate_child_rel(klass=child_relationship_class, param=child_relationship_param)
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
                    result.t1_child_rel = ChildRelationship.create(klass=orig.t1_child_rel.__class__,
                                                                   parent=result.t1,
                                                                   child=result.down.t1,
                                                                   param=orig.t1_child_rel.param)
                if orig.t2_child_rel is not None:
                    result.t2_child_rel = ChildRelationship.create(klass=orig.t2_child_rel.__class__,
                                                                   parent=result.t2,
                                                                   child=result.down.t2,
                                                                   param=orig.t2_child_rel.param)

            # descend to next level
            orig = orig.down
            if result.down is not None:
                result = result.down
        return result


class ChildRelationship(object):
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
        # The parent object of this relationship, e.g. a dict
        self.parent = parent

        # The child object of this relationship, e.g. a value in a dict
        self.child = child

        # A subclass-dependent parameter describing how to get from parent to child, e.g. the key in a dict
        self.param = param

    def __repr__(self):
        name = "<{} id:{}, parent:{}, child:{}, param:{}>"
        parent = short_repr(self.parent)
        child = short_repr(self.child)
        param = short_repr(self.param)
        return name.format(self.__class__.__name__, id(self), parent, child, param)

    def get_partial(self, force=None):
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
        stringified = self.param_to_partial(force)
        if stringified:
            return self.format_partial(stringified)

    @abstractmethod
    def format_partial(self, partial):  # pragma: no cover
        """
        Formats a get partial to create a valid partial python string representing this relationship.
        E.g. for a dict, this turns a partial param "42" into "[42]".
        """
        pass

    def param_to_partial(self, force=None):
        """
        Convert param to a string. Return None if there is no string representation.
        This is called by get_partial()
        :param force: Bends the meaning of "no string representation".
                      If None:
                        Will strictly return Python-parsable expressions. The result those yield will compare
                        equal to the objects in question.
                      If 'yes':
                        Will return '(unrepresentable)' instead of None if there is no string representation
        """
        param = self.param
        if isinstance(param, strings):
            result = self._emphasize_str(param)
        else:
            candidate = str(param)
            try:
                resurrected = literal_eval(candidate)
                # Note: This will miss string-representable custom objects.
                # However, the only alternative I can currently think of is using eval() which is inherently dangerous.
            except (SyntaxError, ValueError):
                result = self.__param_unparsable(param, force)
            else:
                if resurrected == param:
                    result = candidate
                else:
                    result = self.__param_unparsable(param, force)
        return result

    def _emphasize_str(self, string):
        """
        This is a hook allowing subclasses to manipulate param strings.
        :param string: Input string
        :return: Manipulated string, as appropriate in this context.
        """
        return string

    @staticmethod
    def __param_unparsable(param, force=None):
        """Partial called by param_to_partial()"""
        if force == 'yes':
            return '(unrepresentable)'
        else:
            return None


class DictRelationship(ChildRelationship):
    def format_partial(self, partial):
        return "[%s]" % partial

    def _emphasize_str(self, string):
        """Overriding this b/c strings as dict keys must come in quotes."""
        return "'%s'" % string


class SubscriptableIterableRelationship(DictRelationship):
    pass  # for our purposes, we can see lists etc. as special cases of dicts


class InaccessibleRelationship(ChildRelationship):
    def format_partial(self, partial):
        return None

    def get_partial(self, force=None):
        if force == 'yes':
            return "(unrepresentable)"
        else:
            return None


class SetRelationship(InaccessibleRelationship):  # there is no random access to set elements
    pass


class NonSubscriptableIterableRelationship(InaccessibleRelationship):
    def get_partial(self, force=None):
        if force == 'yes':
            return "(unrepresentable)"
        elif force == 'fake' and self.param:
            stringified = self.param_to_partial()
            if stringified:
                return "[%s]" % stringified
        elif force == 'fake':
            return "[(unrepresentable)]"
        else:
            return None


class AttributeRelationship(ChildRelationship):
    def format_partial(self, partial):
        return ".%s" % partial
