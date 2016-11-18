#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from deepdiff.helper import short_repr


class HelperTestCase(unittest.TestCase):
    """Helper Tests."""

    def test_short_repr_when_short(self):

        item = {1: 2}
        output = short_repr(item)
        self.assertEqual(output, '{1: 2}')

    def test_short_repr_when_long(self):

        item = {1: 2, '2': 'Forward Research Manager'}
        output = short_repr(item)
        self.assertEqual(output, "{1: 2, '2': ...}")
