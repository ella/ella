# -*- coding: utf-8 -*-

from ella.articles.models import Article

from example_project.tests.test_newman.helpers import NewmanTestCase

class TestArticleBasics(NewmanTestCase):

    def test_article_saving(self):
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
                'placement_set-0-category' : ('we',)
            }
        
        self.fill_suggest_fields(suggest_data)

        calendar_data = {
            "publish_from" : {
                "day" : "1",
            },
            "publish_to" : {
                "day" : "3",
            }

        }

        self.fill_calendar_fields(calendar_data)

        self.save_form()

        self.assert_equals(u"Article: "+data['title'], s.get_text(self.get_listing_object()+"/th/a[@class='hashadr']"))

        # verify save
        self.assert_equals(1, Article.objects.count())
        a = Article.objects.all()[0]
        self.assert_equals(data['title'], a.title)
        # FIXME: hack, use django-markup
        self.assert_equals('<p>%s</p>\n' % data['description'], a.description)
        self.assert_equals(2, a.authors.count())

