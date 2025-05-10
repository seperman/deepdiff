from deepdiff import DeepDiff
from deepdiff.helper import COLORED_VIEW
from deepdiff.colored_view import RED, GREEN, RESET

def test_colored_view_basic():
    t1 = {
        "name": "John",
        "age": 30,
        "gender": "male",
        "scores": [1, 2, 3],
        "address": {
            "city": "New York",
            "zip": "10001",
        },
    }

    t2 = {
        "name": "John",
        "age": 31,  # Changed
        "scores": [1, 2, 4],  # Changed
        "address": {
            "city": "Boston",  # Changed
            "zip": "10001",
        },
        "team": "abc",  # Added
    }

    diff = DeepDiff(t1, t2, view=COLORED_VIEW)
    result = str(diff)

    expected = f'''{{
  "name": "John",
  "age": {RED}30{RESET} -> {GREEN}31{RESET},
  "scores": [
    1,
    2,
    {RED}3{RESET} -> {GREEN}4{RESET}
  ],
  "address": {{
    "city": {RED}"New York"{RESET} -> {GREEN}"Boston"{RESET},
    "zip": "10001"
  }},
  {GREEN}"team": {GREEN}"abc"{RESET}{RESET},
  {RED}"gender": {RED}"male"{RESET}{RESET}
}}'''
    assert result == expected

def test_colored_view_nested_changes():
    t1 = {
        "level1": {
            "level2": {
                "level3": {
                    "level4": True
                }
            }
        }
    }

    t2 = {
        "level1": {
            "level2": {
                "level3": {
                    "level4": False
                }
            }
        }
    }

    diff = DeepDiff(t1, t2, view=COLORED_VIEW)
    result = str(diff)

    expected = f'''{{
  "level1": {{
    "level2": {{
      "level3": {{
        "level4": {RED}true{RESET} -> {GREEN}false{RESET}
      }}
    }}
  }}
}}'''
    assert result == expected

def test_colored_view_list_changes():
    t1 = [1, 2, 3, 4]
    t2 = [1, 5, 3, 6]

    diff = DeepDiff(t1, t2, view=COLORED_VIEW)
    result = str(diff)

    expected = f'''[
  1,
  {RED}2{RESET} -> {GREEN}5{RESET},
  3,
  {RED}4{RESET} -> {GREEN}6{RESET}
]'''
    assert result == expected

def test_colored_view_list_deletions():
    t1 = [1, 2, 3, 4, 5, 6]
    t2 = [2, 4]

    diff = DeepDiff(t1, t2, view=COLORED_VIEW)
    result = str(diff)

    expected = f'''[
  {RED}1{RESET},
  2,
  {RED}3{RESET},
  4,
  {RED}5{RESET},
  {RED}6{RESET}
]'''
    assert result == expected

def test_colored_view_with_ignore_order():
    t1 = [1, 2, 3]
    t2 = [3, 2, 1]

    diff = DeepDiff(t1, t2, view=COLORED_VIEW, ignore_order=True)
    result = str(diff)

    expected = '''[
  3,
  2,
  1
]'''
    assert result == expected

def test_colored_view_with_empty_diff():
    t1 = {"a": 1, "b": 2}
    t2 = {"a": 1, "b": 2}

    diff = DeepDiff(t1, t2, view=COLORED_VIEW)
    result = str(diff)

    expected = '''{
  "a": 1,
  "b": 2
}'''
    assert result == expected
