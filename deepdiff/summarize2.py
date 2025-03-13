from deepdiff.helper import JSON
from deepdiff.serialization import json_dumps

# type edge_weight_child_strcuture = tuple[int, int, Any]

# Function to calculate node weights recursively
def calculate_weights(node):# -> tuple[int, tuple[str, edge_weight_child_strcuture]]:
    if isinstance(node, dict):
        weight = 0
        children_weights = {}
        for k, v in node.items():
            edge_weight = len(k)
            child_weight, child_structure = calculate_weights(v)
            total_weight = edge_weight + child_weight
            weight += total_weight
            children_weights[k] = (edge_weight, child_weight, child_structure)
        return weight, ('dict', children_weights)

    elif isinstance(node, list):
        weight = 0
        children_weights = []
        for v in node:
            edge_weight = 0  # As per updated instruction, indexes have zero weight
            child_weight, child_structure = calculate_weights(v)
            total_weight = edge_weight + child_weight
            weight += total_weight
            children_weights.append((edge_weight, child_weight, child_structure))
        return weight, ('list', children_weights)

    else:
        if isinstance(node, str):
            node_weight = len(node)
        elif isinstance(node, int):
            node_weight = len(str(node))
        elif isinstance(node, float):
            node_weight = len(str(round(node, 2)))
        elif node is None:
            node_weight = 1
        else:
            node_weight = 0
        return node_weight, ('leaf', node)


def _truncate(s: str, max_len: int) -> str:
    """
    Truncate string s to max_len characters.
    If possible, keep the first (max_len-5) characters, then '...' then the last 2 characters.
    """
    if len(s) <= max_len:
        return s
    if max_len <= 5:
        return s[:max_len]
    return s[:max_len - 5] + "..." + s[-2:]


# Greedy algorithm to shrink the tree
def shrink_tree(node_structure, max_weight: int) -> tuple[JSON, int]:
    node_type, node_info = node_structure

    if node_type == 'leaf':
        leaf_value = node_info
        leaf_weight, _ = calculate_weights(leaf_value)
        if leaf_weight <= max_weight:
            return leaf_value, leaf_weight
        else:
            # Truncate leaf value if string
            if isinstance(leaf_value, str):
                truncated_value = _truncate(leaf_value, max_weight)
                return truncated_value, len(truncated_value)
            # For int or float, convert to string and truncate
            elif isinstance(leaf_value, (int, float)):
                leaf_str = str(leaf_value)
                truncated_str = leaf_str[:max_weight]
                # Convert back if possible
                try:
                    return int(truncated_str), len(truncated_str)
                except Exception:
                    try:
                        return float(truncated_str), len(truncated_str)
                    except Exception:
                        return truncated_str, len(truncated_str)
            elif leaf_value is None:
                return None, 1 if max_weight >=1 else 0

    elif node_type == 'dict':
        shrunk_dict = {}
        total_weight = 0
        # Sort children by weight (heavy first)
        sorted_children = sorted(node_info.items(), key=lambda x: x[1][0] + x[1][1], reverse=True)
        for k, (edge_w, child_w, child_struct) in sorted_children:
            if total_weight + edge_w >= max_weight:
                continue  # Skip heavy edge entirely
            remaining_weight = max_weight - total_weight - edge_w
            shrunk_child, shrunk_weight = shrink_tree(child_struct, remaining_weight)
            if shrunk_child is not None:
                shrunk_dict[k[:edge_w]] = shrunk_child
                total_weight += edge_w + shrunk_weight
            if total_weight >= max_weight:
                break
        return shrunk_dict, total_weight

    elif node_type == 'list':
        shrunk_list = []
        total_weight = 0
        # Sort children by weight (heavy first)
        sorted_children = sorted(node_info, key=lambda x: x[0] + x[1], reverse=True)
        for edge_w, child_w, child_struct in sorted_children:
            remaining_weight = max_weight - total_weight
            shrunk_child, shrunk_weight = shrink_tree(child_struct, remaining_weight)
            if shrunk_child is not None:
                shrunk_list.append(shrunk_child)
                total_weight += shrunk_weight
            if total_weight >= max_weight - 1:
                shrunk_list.append('...')
                break
        return shrunk_list, total_weight
    return None, 1

# Main function to summarize the tree
def summarize_tree(tree: dict | list, max_weight: int) -> JSON:
    total_weight, tree_structure = calculate_weights(tree)
    if total_weight <= max_weight:
        return tree  # No need to shrink
    shrunk_tree, _ = shrink_tree(tree_structure, max_weight)
    return shrunk_tree

# Exposed function for user convenience
def summarize(json_data, max_length=200) -> str:
    return json_dumps(summarize_tree(json_data, max_length))
