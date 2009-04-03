# -*- coding: utf-8 -*-
from djangosanetesting import UnitTestCase

class TestBasicAsserts(UnitTestCase):
    def test_assert_equals(self):
        self.assert_equals(1, 1)