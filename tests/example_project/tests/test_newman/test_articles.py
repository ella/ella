# -*- coding: utf-8 -*-
from copy import copy
from datetime import datetime
from time import strftime

from django.utils.translation import ugettext_lazy as _

from ella.articles.models import Article

from example_project.tests.test_newman.helpers import (
    NewmanTestCase,
    DateTimeAssert,
)

class TestArticleBasics(NewmanTestCase):
    translation_language_code = 'cs'
    make_translation = True

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
            'slug' : u'title',
        }
        self.fill_fields(data)

        expected_data = copy(data)

        # fill in the suggesters
        suggest_data = {
            'category': ('we',),
            'authors':  ('Bar', 'Kin',),
            'placement_set-0-category' : ('we',)
        }
        self.fill_suggest_fields(suggest_data)

        self.fill_using_lookup({
            "authors" : u"King Albert II",
        })

        expected_data.update({
            'category' : [u"Africa/west-africa"],
            'authors' : [u"Barack Obama", u"King Albert II"],
            'placement_set-0-category' : [u"Africa/west-africa"],
        })
        

        calendar_data = {
            "publish_from" : {
                "day" : "1",
            },
            "publish_to" : {
                "day" : "3",
            }

        }

        self.fill_calendar_fields(calendar_data)

        # TODO: Replace fuzzy matching when it will be decided how to insert time
        expected_data.update({
            "placement_set-0-publish_from" : DateTimeAssert(datetime(
                year = int(strftime("%Y")),
                month = int(strftime("%m")),
                day = int(calendar_data['publish_from']['day']),
                hour = int(strftime("%H")),
                minute = int(strftime("%M")),
            )),

            "placement_set-0-publish_to" : DateTimeAssert(datetime(
                year = int(strftime("%Y")),
                month = int(strftime("%m")),
                day = int(calendar_data['publish_to']['day']),
                hour = int(strftime("%H")),
                minute = int(strftime("%M")),
            )),
        })

        self.save_form()
        self.assert_equals(u"%s: %s" % (unicode(_(u"Article")), data['title']), s.get_text(self.get_listing_object()+"/th/a[@class='hashadr']"))

        # verify save on list
        self.assert_equals(1, Article.objects.count())
        a = Article.objects.all()[0]
        self.assert_equals(data['title'], a.title)

        self.assert_equals('<p>%s</p>\n' % data['description'], a.description)
        self.assert_equals(2, a.authors.count())

        # verify all fields
        s.click(self.get_listing_object()+"/th/a[@class='hashadr']")
        
        self.verify_form(expected_data)

    def test_resume_ability_after_500(self):
        s = self.selenium

        # go to article adding
        s.click(self.elements['navigation']['articles'])
        s.click(self.elements['controls']['add'])

        # wait for the page to fully load
        s.wait_for_element_present(self.elements['controls']['suggester'])

        # fill the form that will produce 500 (because of non-numeric photo)
        data = {
            'photo' : u'马 žš experiment',
            'upper_title' : u'vyšší',
            'description' : u'Article description',
            'slug' : u'title',
        }
        expected_data = copy(data)
        self.fill_fields(data)

        data = {
            "authors" : u"King Albert II",
            'category' : u"Africa/central-africa",
        }
        expected_data.update(dict([(key, [data[key]])for key in data]))
        self.fill_using_lookup(data)
        self.save_form()

        # now to to add article again
        s.click(self.elements['navigation']['articles'])
        s.click(self.elements['controls']['add'])

        s.wait_for_element_present("id_drafts")

        # load template
        s.select("id_drafts", "index=1")

        s.wait_for_condition("selenium.page().getElementById('id_slug').innerHTML != ''", 30000);

        # and check we have data we've stored
        self.verify_form(expected_data)

        # let selenium grab window again...
        #FIXME: This is hacky and some wait_for_condition should be found; however,
        # selenium.page().getCurrentWindow != null is not working...:]
        from time import sleep
        sleep(5)
