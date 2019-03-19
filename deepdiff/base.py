from ordered_set import OrderedSet
from deepdiff.helper import strings, numbers


DEFAULT_SIGNIFICANT_DIGITS_WHEN_IGNORE_NUMERIC_TYPES = 55


class Base:
    numbers = numbers
    strings = strings

    def get_significant_digits(self, significant_digits, ignore_numeric_type_changes):
        if ignore_numeric_type_changes and not significant_digits:
            significant_digits = DEFAULT_SIGNIFICANT_DIGITS_WHEN_IGNORE_NUMERIC_TYPES
        if significant_digits is not None and significant_digits < 0:
            raise ValueError(
                "significant_digits must be None or a non-negative integer")
        return significant_digits

    def get_ignore_types_in_groups(self, ignore_type_in_groups,
                                   ignore_string_type_changes,
                                   ignore_numeric_type_changes):
        if ignore_type_in_groups:
            if isinstance(ignore_type_in_groups[0], type):
                ignore_type_in_groups = [OrderedSet(ignore_type_in_groups)]
            else:
                ignore_type_in_groups = list(map(OrderedSet, ignore_type_in_groups))
        else:
            ignore_type_in_groups = []

        if ignore_string_type_changes and self.strings not in ignore_type_in_groups:
            ignore_type_in_groups.append(OrderedSet(self.strings))

        if ignore_numeric_type_changes and self.numbers not in ignore_type_in_groups:
            ignore_type_in_groups.append(OrderedSet(self.numbers))

        return ignore_type_in_groups
