# -*- coding: utf-8 -*-


class CustomClass:
    def __init__(self, a, b=None):
        self.a = a
        self.b = b

    def __str__(self):
        return "({}, {})".format(self.a, self.b)

    def __repr__(self):
        return self.__str__()
