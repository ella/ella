# -*- coding: utf-8 -*-

from ella.articles.models import Article

from example_project.tests.test_newman.helpers import NewmanTestCase

class TestArticleBasics(NewmanTestCase):

    def test_article_template_saving(self):
        s = self.selenium

        # go to article adding
        s.click(self.elements['navigation']['articles'])
        s.click(self.elements['controls']['add'])

        # wait for the page to fully load
        s.wait_for_element_present(self.elements['controls']['suggester'])

        # fill the form
        data = {
                'title' : u'马 žš experiment',
                'upper_title' : u'vyšší',
                'description' : u'Article description',
                'slug' : 'title',
            }
        self.fill_fields(data)

        # fill in the suggesters
        suggest_data = {
                'category': ('we',),
                'authors':  ('Bar', 'Kin',),
            }
        self.fill_suggest_fiels(suggest_data)

        self.save_form()


        # verify save
        self.assert_equals(1, Article.objects.count())
        a = Article.objects.all()[0]
        self.assert_equals(data['title'], a.title)
        # FIXME: hack, use django-markup
        self.assert_equals('<p>%s</p>\n' % data['description'], a.description)
        self.assert_equals(2, a.authors.count())




