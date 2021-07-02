import re


class BaseOperator:
    __operator_name__ = "__base__"

    def __init__(self, path_regex):
        self.path_regex = path_regex
        self.regex = re.compile(f"^{self.path_regex}$")

    def match(self, level) -> bool:
        matched = re.search(self.regex, level.path()) is not None
        return matched

    def diff(self, level, instance) -> bool:
        raise NotImplementedError
