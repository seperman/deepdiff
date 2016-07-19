from copy import copy


class DeepSet(set):
    def __init__(self, *args):
        if len(args) == 0:
            pass
        elif len(args) > 1:
            self.__init_direct_values(args)
        else:
            try: # is it iterable or a direct value?
                test = iter(args[0])
            except TypeError:
                self.__init_direct_values(args)
            else:
                super(DeepSet, self).__init__(args[0])

    def __init_direct_values(self, *args):
        self.update(*args)

    # First, some of the basic Object methods

    def __str__(self):
        output = "{"

        first_elem = True
        for elem in self:
            if first_elem:
                first_elem = False
            else:
                output += ", "
            output += str(elem)

        output += "}"
        return output

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        # Get rid of some trivial cases

        if id(self) == id(other):
            return True

        if len(self) != len(other):
            return False


        # TODO optimize: this whole build-a-dict-and-throw-it-away approach doesn't make much sense

        # I'm equal to thas other set if:
        # - all of my elements are included in that other set; and
        # - thas other set contains nothing else
        # This "double" comparison is necessary because our deep comparison logic is not always bijective,
        # e.g. I may contain different elements that are both "equal" to an element of thas other set.

        from .deepdiff import DeepDiff
        other = DeepSet(other) # just our working copy

        for my_elem in self:         # compare each of my elements...

            is_included = False
            for other_elem in other: # ...to each of the other elements
                #print("Comparing " + str(my_elem) + " with " + str(other_elem) + ".")
                diff = DeepDiff(my_elem, other_elem)
                if diff == {}:
                    is_included = True
                    other.discard(my_elem) # remove from our working copy of "other"
                    break
                else:
                    continue

            if not is_included:
                return False

        if len(other) == 0: # we're only equal if there are no additional elements in that other set
            return True
        else:
            return False

    def __ne__(self, other):
        return not self == other


    # methods in the order they are documented at https://docs.python.org/3.5/library/stdtypes.html#set

    # len() can be inherited

    # x in s

    # First, here's our custom method that return the *actual contained* object if it is equal to item.
    # Notice this is a special case a regular set doesn't need to handle
    def __contains_return__(self, item):
        from .deepdiff import DeepDiff
        for element in self:
            diff = DeepDiff(element, item)
            if diff == {}:
                #print(str(self) + " DOES contain " + str(item))
                return element
        #print(str(self) + " does not contain " + str(item))
        return False

    # now implement the actual __contains__ method
    def __contains__(self, item):
        if self.__contains_return__(item) == False:
            return False
        else:
            return True

    # "x not in s" is the inversion of the above

    # isdisjoint()
    def isdisjoint(self, other):
        if (self & other) == {}:
            return True
        else:
            return False

    # issubset(), <= ?!
    def issubset(self, other):
        for element in self:
            if element not in other:
                #print(str(element) + " is not in " + str(other))
                return False
        return True

    def __le__(self, other):
        return self.issubset(other)

    def __lt__(self, other):
        return self <= other and self != other

    # TODO: issuperset, >= ?!

    # TODO: union?!

    # intersection, operator &
    def intersection(self, other):
        result = DeepSet()
        for element in self:
            if element in other:
                result.add(element)
        return result

    def __and__(self, other):
        return self.intersection(other)

    # difference(), -
    def __sub__(self, other):
        if id(self) == id(other):
            return DeepSet({})

        result = copy(self)
        for other_elem in other:
            if other_elem in self:
                result.remove(other_elem)
        #print(str(self) + " - " + str(other) + " = " + str(result))
        return result

    def __rsub__(self, other):
        #print("RSUB!")
        return other.__sub__(self)


    # TODO: symmetric_difference, ^ ?!

    # copy() can be inherited

    # TODO: update() can be inherited?!

    # TODO: intersection_update() ?!

    # TODO: difference_update() ?!

    # TODO: symmetric_difference_update() ?!

    # add() can be inherited

    # remove()
    def remove(self, elem):
        to_remove = self.__contains_return__(elem)
        if to_remove:
            return super(DeepSet, self).remove(to_remove)
        else:
            raise KeyError

    # discard()
    def discard(self, elem):
        try:
            return self.remove(elem)
        except KeyError:
            return False

    # pop() can be inherited

    # clear() can be inherited


    # Finally, some additional functionality

    def diff(self, other):
        """
        Compare this set to another one and return a dictionary of all changes.
        See deepdiff for details.
        """
        from .deepdiff import DeepDiff
        return DeepDiff(self, other)
