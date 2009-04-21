# -*- coding: utf-8 -*-

from example_project.tests.test_newman.helpers import NewmanTestCase

class TestArticleBasics(NewmanTestCase):

    def test_article_template_saving(self):
        s = self.selenium

        # go to article adding
        s.click(self.elements['navigation']['article_add'])

        # prepare article structure for me

        # fill the form
        article = {
            'title' : u'马 experiment',
            'upper_title' : u'vyšší',
        }
        