from typing import Any
from deepdiff.serialization import json_dumps


def _truncate(s, max_len):
    """
    Truncate string s to max_len characters.
    If possible, keep the first (max_len-5) characters, then '...' then the last 2 characters.
    """
    if len(s) <= max_len:
        return s
    if max_len <= 5:
        return s[:max_len]
    return s[:max_len - 5] + "..." + s[-2:]

class JSONNode:
    def __init__(self, data: Any, key=None):
        """
        Build a tree node for the JSON data.
        If this node is a child of a dict, key is its key name.
        """
        self.key = key
        self.children_list: list[JSONNode] = []
        self.children_dict: list[tuple[Any, JSONNode]] = []
        if isinstance(data, dict):
            self.type = "dict"
            # Preserve insertion order: list of (key, child) pairs.
            for k, v in data.items():
                child = JSONNode(v, key=k)
                self.children_dict.append((k, child))
        elif isinstance(data, list):
            self.type = "list"
            self.children_list = [JSONNode(item) for item in data]
        else:
            self.type = "primitive"
            # For primitives, use json.dumps to get a compact representation.
            try:
                self.value = json_dumps(data)
            except Exception:
                self.value = str(data)
    
    def full_repr(self) -> str:
        """Return the full minimized JSON representation (without trimming) for this node."""
        if self.type == "primitive":
            return self.value
        elif self.type == "dict":
            parts = []
            for k, child in self.children_dict:
                parts.append(f'"{k}":{child.full_repr()}')
            return "{" + ",".join(parts) + "}"
        elif self.type == "list":
            parts = [child.full_repr() for child in self.children_list]
            return "[" + ",".join(parts) + "]"
        return self.value
    
    def full_weight(self):
        """Return the character count of the full representation."""
        return len(self.full_repr())
    
    def _summarize(self, budget) -> str:
        """
        Return a summary string for this node that fits within budget characters.
        The algorithm may drop whole sub-branches (for dicts) or truncate long primitives.
        """
        if self.type == "primitive":
            rep = self.value
            if len(rep) <= budget:
                return rep
            else:
                return _truncate(rep, budget)
        elif self.type == "dict":
            return self._summarize_dict(budget)
        elif self.type == "list":
            return self._summarize_list(budget)
        return self.value
    
    def _summarize_dict(self, budget) -> str:
        # If the dict is empty, return {}
        if not self.children_dict:
            return "{}"
        # Build a list of pairs with fixed parts:
        # Each pair: key_repr is f'"{key}":'
        # Also store the full (untrimmed) child representation.
        pairs = []
        for k, child in self.children_dict:
            key_repr = f'"{k}":'
            child_full = child.full_repr()
            pair_full = key_repr + child_full
            pairs.append({
                "key": k,
                "child": child,
                "key_repr": key_repr,
                "child_full": child_full,
                "pair_full": pair_full,
                "full_length": len(pair_full)
            })
        n = len(pairs)
        fixed_overhead = 2 + (n - 1)  # braces plus commas between pairs
        total_full = sum(p["full_length"] for p in pairs) + fixed_overhead
        # If full representation fits, return it.
        if total_full <= budget:
            parts = [p["key_repr"] + p["child_full"] for p in pairs]
            return "{" + ",".join(parts) + "}"
        
        # Otherwise, try dropping some pairs.
        kept = pairs.copy()
        # Heuristic: while the representation is too long, drop the pair whose child_full is longest.
        while kept:
            # Sort kept pairs in original insertion order.
            kept_sorted = sorted(kept, key=lambda p: self.children_dict.index((p["key"], p["child"])))
            current_n = len(kept_sorted)
            fixed = sum(len(p["key_repr"]) for p in kept_sorted) + (current_n - 1) + 2
            remaining_budget = budget - fixed
            if remaining_budget < 0:
                # Not enough even for fixed costs; drop one pair.
                kept.remove(max(kept, key=lambda p: len(p["child_full"])))
                continue
            total_child_full = sum(len(p["child_full"]) for p in kept_sorted)
            # Allocate available budget for each child's summary proportionally.
            child_summaries = []
            for p in kept_sorted:
                ideal = int(remaining_budget * (len(p["child_full"]) / total_child_full)) if total_child_full > 0 else 0
                summary_child = p["child"]._summarize(ideal)
                child_summaries.append(summary_child)
            candidate = "{" + ",".join([p["key_repr"] + s for p, s in zip(kept_sorted, child_summaries)]) + "}"
            if len(candidate) <= budget:
                return candidate
            # If still too long, drop the pair with the largest child_full length.
            to_drop = max(kept, key=lambda p: len(p["child_full"]))
            kept.remove(to_drop)
        # If nothing remains, return a truncated empty object.
        return _truncate("{}", budget)
    
    def _summarize_list(self, budget) -> str:
        # If the list is empty, return []
        if not self.children_list:
            return "[]"
        full_repr = self.full_repr()
        if len(full_repr) <= budget:
            return full_repr
        # For lists, show only the first element and an omission indicator if more elements exist.
        suffix = ",..." if len(self.children_list) > 1 else ""
        inner_budget = budget - 2 - len(suffix)  # subtract brackets and suffix
        first_summary = self.children_list[0]._summarize(inner_budget)
        candidate = "[" + first_summary + suffix + "]"
        if len(candidate) <= budget:
            return candidate
        return _truncate(candidate, budget)


def summarize(data, max_length=200):
    """
    Build a tree for the given JSON-compatible data and return its summary,
    ensuring the final string is no longer than self.max_length.
    """
    root = JSONNode(data)
    return root._summarize(max_length).replace("{,", "{")
