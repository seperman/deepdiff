from deepdiff.deephash import DeepHash
from deepdiff.helper import DELTA_VIEW, numbers, strings, add_to_frozen_set, get_numeric_types_distance, not_found
from collections.abc import Mapping, Iterable

DISTANCE_CALCS_MSG = (
    'Only during the hash calculations, the objects hierarchical '
    'counts are evaluated. As a result, the deep distance is only calculated when ignore_order=True.'
    'If you have a usage for this function when ignore_order=False, then let us know.')


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

        Note: The deep distance calculations are currently only internally used when ignore_order=True so
        it is implemented as a part of an algorithm that ONLY runs when ignore_order=True.
        It DOES NOT work properly when ignore_order=False (default).
        If you have a use case for the deep distance to be calculated when ignore_order=False, then please open a ticket.

        Info: The current algorithm is based on the number of operations that are needed to convert t1 to t2 divided
        by the number of items that make up t1 and t2.
        """
        # if not self.hashes or not self.ignore_order:
        #     raise ValueError(DISTANCE_CALCS_MSG)

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
    if hasattr(item, '_diff_length'):
        length = item._diff_length
    elif isinstance(item, Mapping):
        for key, subitem in item.items():
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
                if parents_ids and item_id in parents_ids:
                    continue
                parents_ids_added = add_to_frozen_set(parents_ids, item_id)
                length += _get_item_length(subitem, parents_ids_added)

    try:
        item._diff_length = length
    except Exception:
        pass
    return length
