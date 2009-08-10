# -*- coding: utf-8 -*-
import re

from django.utils.translation import ugettext_lazy as _
from djangosanetesting import UnitTestCase

from example_project.tests.test_newman.helpers import NewmanTestCase

def get_category_count_from_paginator_text(text, placement_name):
    return int(re.findall('([0-9]+) %s' % placement_name, text)[0])

class TestCategoryCount(UnitTestCase):
    def test_returns_correct_cat_count(self):
        self.assert_equals(41, get_category_count_from_paginator_text('1 \n\n 2 \n\n\n41 %s\n  Show all' % unicode(_(u"categories")),
            placement_name=unicode(_(u"categories"))))

    def test_returns_correct_cat_count_if_number_first(self):
        self.assert_equals(6, get_category_count_from_paginator_text('6 %s' % unicode(_(u"categories")),
            placement_name=unicode(u"categories")))

    def test_raises_error_on_empty_input(self):
        self.assert_raises(Exception, get_category_count_from_paginator_text, '')

    def test_raises_error_on_incorrect_input(self):
        self.assert_raises(Exception, get_category_count_from_paginator_text, 'no 12 %s count here 34 23' % "category",
            placement_name=unicode(_(u"categories")))

class TestCategoryAdmin(NewmanTestCase):

    def test_category_list(self):
        s = self.selenium
        s.click(self.elements['navigation']['categories'])
        self.assert_equals(41, get_category_count_from_paginator_text(s.get_text(self.elements['controls']['paginator_top']),
            placement_name=unicode(_(u"Categories"))))

    def test_filter_categories_by_site(self):
        s = self.selenium
        s.click(self.elements['navigation']['categories'])
        s.click(self.elements['controls']['show_filters'])
        s.click("//div[@id='filters']//a[@class='btn combo']")
        s.click("//div[@id='filters']//ul/li/a")
        s.wait_for_element_present("//input[@name='site__id__exact' and @type='hidden' and @value='1']")

        # check the correct object count
        self.assert_equals(6, get_category_count_from_paginator_text(s.get_text(self.elements['controls']['paginator_top']),
            placement_name=unicode(_(u"Categories"))))
        # check the filter on light is on
        self.assert_equals(u"%s (%s)" % (unicode(_(u'Filters')), unicode(_(u'on!'))),
            s.get_text(self.elements['controls']['show_filters']))

