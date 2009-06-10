from datetime import datetime, timedelta

from djangosanetesting.cases import UnitTestCase

from example_project.tests.test_newman.helpers import (
    DateTimeAssert,
)

class TestCustomAssertions(UnitTestCase):

    def test_date_differences_success(self):
        custom = DateTimeAssert(datetime(year=2008, month=2, day=15, hour=12, minute=40))
        self.assert_true(custom.is_equal("2008-02-15 12:41"))

    def test_date_differences_too_big_difference(self):
        custom = DateTimeAssert(datetime(year=2008, month=2, day=15, hour=12, minute=40))
        self.assert_false(custom.is_equal("2009-10-12 13:33"))

    def test_date_differences_success_with_custom_diff(self):
        custom = DateTimeAssert(datetime(year=2008, month=2, day=15, hour=12, minute=40),
            allowed_delta=timedelta(weeks=120))
        self.assert_true(custom.is_equal("2009-10-12 13:33"))
