import datetime
from deepdiff.deephash import DeepHash
from deepdiff.helper import DELTA_VIEW, numbers, strings, add_to_frozen_set, not_found, only_numbers
from collections.abc import Mapping, Iterable


class DistanceMixin:

    def get_deep_distance(self):
        """
        Gives a numeric value for the distance of t1 and t2 based on how many operations are needed to convert
        one to the other.

        This is a similar concept to the Levenshtein Edit Distance but for the structured data and is it is designed
        to be between 0 and 1.

        A distance of zero means the objects are equal and a distance of 1 is very far.

        Note: The distance calculation formula is subject to change in future. Use the distance results only as a
        way of comparing the distances of pairs of items with other pairs rather than an absolute distance
        such as the one provided by Levenshtein edit distance.

        Info: The current algorithm is based on the number of operations that are needed to convert t1 to t2 divided
        by the number of items that make up t1 and t2.
        """

        _distance = get_numeric_types_distance(
            self.t1, self.t2, max_=self.cutoff_distance_for_pairs)
        if _distance is not not_found:
            return _distance

        item = self if self.view == DELTA_VIEW else self._to_delta_dict(report_repetition_required=False)
        diff_length = _get_item_length(item)

        if diff_length == 0:
            return 0

        t1_len = self.__get_item_rough_length(self.t1)
        t2_len = self.__get_item_rough_length(self.t2)

        return diff_length / (t1_len + t2_len)

    def __get_item_rough_length(self, item, parent='root'):
        """
        Get the rough length of an item.
        It is used as a part of calculating the rough distance between objects.

        **parameters**

        item: The item to calculate the rough length for
        parent: It is only used for DeepHash reporting purposes. Not really useful here.
        """
        length = DeepHash.get_key(self.hashes, key=item, default=None, extract_index=1)
        if length is None:
            self.__calculate_item_deephash(item)
            length = DeepHash.get_key(self.hashes, key=item, default=None, extract_index=1)
        return length

    def __calculate_item_deephash(self, item):
        DeepHash(
            item,
            hashes=self.hashes,
            parent='root',
            apply_hash=True,
            **self.deephash_parameters,
        )


def _get_item_length(item, parents_ids=frozenset([])):
    """
    Get the number of operations in a diff object.
    It is designed mainly for the delta view output
    but can be used with other dictionary types of view outputs too.
    """
    length = 0
    if isinstance(item, Mapping):
        for key, subitem in item.items():
            # dedupe the repetition report so the number of times items have shown up does not affect the distance.
            if key in {'iterable_items_added_at_indexes', 'iterable_items_removed_at_indexes'}:
                new_subitem = {}
                for path_, indexes_to_items in subitem.items():
                    used_value_ids = set()
                    new_indexes_to_items = {}
                    for k, v in indexes_to_items.items():
                        v_id = id(v)
                        if v_id not in used_value_ids:
                            used_value_ids.add(v_id)
                            new_indexes_to_items[k] = v
                    new_subitem[path_] = new_indexes_to_items
                subitem = new_subitem

            # internal keys such as _numpy_paths should not count towards the distance
            if isinstance(key, strings) and key.startswith('_'):
                continue

            item_id = id(subitem)
            if parents_ids and item_id in parents_ids:
                continue
            parents_ids_added = add_to_frozen_set(parents_ids, item_id)
            length += _get_item_length(subitem, parents_ids_added)
    elif isinstance(item, numbers):
        length = 1
    elif isinstance(item, strings):
        length = 1
    elif isinstance(item, Iterable):
        for subitem in item:
            item_id = id(subitem)
            if parents_ids and item_id in parents_ids:
                continue
            parents_ids_added = add_to_frozen_set(parents_ids, item_id)
            length += _get_item_length(subitem, parents_ids_added)
    elif isinstance(item, type):  # it is a class
        length = 1
    else:
        if hasattr(item, '__dict__'):
            for subitem in item.__dict__:
                item_id = id(subitem)
                parents_ids_added = add_to_frozen_set(parents_ids, item_id)
                length += _get_item_length(subitem, parents_ids_added)
    return length


def time_to_seconds(t):
    return (t.hour * 60 + t.minute) * 60 + t.second


def _get_numbers_distance(num1, num2, max_=1):
    """
    Get the distance of 2 numbers. The output is a number between 0 to the max.
    The reason is the
    When max is returned means the 2 numbers are really far, and 0 means they are equal.
    """
    try:
        # Since we have a default cutoff of 0.3 distance when
        # getting the pairs of items during the ingore_order=True
        # calculations, we need to make the divisor of comparison very big
        # so that any 2 numbers can be chosen as pairs.
        divisor = (num1 + num2) / max_
    except Exception:
        return max_
    else:
        if not divisor:
            return max_
        try:
            return min(max_, abs((num1 - num2) / divisor))
        except Exception:  # pragma: no cover. I don't think this line will ever run but doesn't hurt to leave it.
            return max_  # pragma: no cover


def _get_datetime_distance(date1, date2, max_):
    return _get_numbers_distance(date1.timestamp(), date2.timestamp(), max_)


def _get_date_distance(date1, date2, max_):
    return _get_numbers_distance(date1.toordinal(), date2.toordinal(), max_)


def _get_timedelta_distance(timedelta1, timedelta2, max_):
    return _get_numbers_distance(timedelta1.total_seconds(), timedelta2.total_seconds(), max_)


def _get_time_distance(time1, time2, max_):
    return _get_numbers_distance(time_to_seconds(time1), time_to_seconds(time2), max_)


TYPES_TO_DIST_FUNC = [
    (only_numbers, _get_numbers_distance),
    (datetime.datetime, _get_datetime_distance),
    (datetime.date, _get_date_distance),
    (datetime.timedelta, _get_timedelta_distance),
    (datetime.time, _get_time_distance),
]


def get_numeric_types_distance(num1, num2, max_):
    for type_, func in TYPES_TO_DIST_FUNC:
        if isinstance(num1, type_) and isinstance(num2, type_):
            return func(num1, num2, max_)
    return not_found
