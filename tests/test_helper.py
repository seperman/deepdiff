#!/usr/bin/env python
# -*- coding: utf-8 -*-
from deepdiff.helper import short_repr


class TestHelper:
    """Helper Tests."""

    def test_short_repr_when_short(self):

        item = {1: 2}
        output = short_repr(item)
        assert output == '{1: 2}'

    def test_short_repr_when_long(self):

        item = {'Eat more': 'burritos'}
        output = short_repr(item)
        assert output == "{'Eat more':...}"
