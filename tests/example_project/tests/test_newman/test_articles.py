# -*- coding: utf-8 -*-

from ella.articles.models import Article

from example_project.tests.test_newman.helpers import NewmanTestCase

class TestArticleBasics(NewmanTestCase):

    def test_article_template_saving(self):
        s = self.selenium

        # go to article adding
        s.click(self.elements['navigation']['article'])
        s.click(self.elements['controls']['add'])

        # wait for the page to fully load
        s.wait_for_element_present(self.elements['controls']['suggester'])

        # prepare article structure for me

        # fill the form
        data = {
                'title' : u'马 experiment',
                'upper_title' : u'vyšší',
                'description' : u'Article description',
                'slug' : 'title',
            }

        for key, value in data.items():
            s.type(key, value)


        # check slug being created


        # fill in the suggesters
        suggest_data = {
                'category': ('we',),
                'authors':  ('Bar', 'Kin',),
            }

        for key, values in suggest_data.items():
            for value in values:
                id = 'id_%s_suggest' % key
                s.click(id)
                s.type(id, value)
                s.click(id)
                s.wait_for_element_present(self.elements['controls']['suggester_visible'])
                s.key_down(id, '\40') # down arrow
                s.click(self.elements['controls']['suggester_visible'])

        # save
        s.click(self.elements['controls']['save'])
        s.wait_for_element_present(self.elements['controls']['message']['ok'])

        
        # verify save
        self.assert_equals(1, Article.objects.count())
        a = Article.objects.all()[0]
        self.assert_equals(data['title'], a.title)
        # FIXME: hack, use django-markup
        self.assert_equals('<p>%s</p>\n' % data['description'], a.description)
        self.assert_equals(2, a.authors.count())

        

        
