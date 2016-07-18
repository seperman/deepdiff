#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
To run the test, run this in the root of repo:
python -m unittest discover

To run a specific test, run this from the root of repo:
python -m unittest tests.DeepDiffTestCase.test_list_of_sets_difference_ignore_order
"""

from sys import version
py3 = version[0] == '3'


class CustomClass:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __str__(self):
        return "(" + str(self.a) + ", " + str(self.b) + ")"

    def __repr__(self):
        return self.__str__()
