# -*- coding: utf-8 -*-
import re

from djangosanetesting import UnitTestCase

from ella.core.models import Category

from example_project.tests.test_newman.helpers import NewmanTestCase

CAT_COUNT = re.compile('([0-9]+) Categories')
def get_category_count_from_paginator_text(text):
    return int(CAT_COUNT.findall(text)[0])

class TestCategoryCount(UnitTestCase):
    def test_returns_correct_cat_count(self):
        self.assert_equals(41, get_category_count_from_paginator_text('1 \n\n 2 \n\n\n41 Categories\n  Show all'))

    def test_returns_correct_cat_count_if_number_first(self):
        self.assert_equals(6, get_category_count_from_paginator_text('6 Categories'))

    def test_raises_error_on_empty_input(self):
        self.assert_raises(Exception, get_category_count_from_paginator_text, '')

    def test_raises_error_on_incorrect_input(self):
        self.assert_raises(Exception, get_category_count_from_paginator_text, 'no 12 category count here 34 23')

class TestCategoryAdmin(NewmanTestCase):
    def test_category_list(self):
        s = self.selenium
        s.click(self.elements['navigation']['categories'])
        self.assert_equals(41, get_category_count_from_paginator_text(s.get_text('//p[@class="paginator"]')))

    def test_filter_categories_by_site(self):
        s = self.selenium
        s.click(self.elements['navigation']['categories'])
        s.click(self.elements['controls']['show_filters'])
        s.click("//div[@id='filters']//a[@class='btn combo']")
        s.click("//div[@id='filters']//ul/li/a")
        s.wait_for_element_present("//input[@name='site__id__exact' and @type='hidden' and @value='1']")

        # check the correct object count
        self.assert_equals(6, get_category_count_from_paginator_text(s.get_text('//p[@class="paginator"]')))

        # check the filter on light is on
        self.assert_equals('Filters (on!)', s.get_text(self.elements['controls']['show_filters']))








