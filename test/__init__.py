#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
To run the test, run this in the root of repo:
python -m unittest discover

To run a specific test, run this from the root of repo:
python -m unittest tests.DeepDiffTestCase.test_list_of_sets_difference_ignore_order
"""

from deepdiff.deepdiff import DeepDiff
from deepdiff.deepset import DeepSet

from .test_deepdiff import *
from .test_deepset import *
