# -*- coding: utf-8 -*-
from copy import copy
from datetime import datetime
from time import strftime, sleep

from django.utils.translation import ugettext_lazy as _

from ella.articles.models import Article

from example_project.tests.test_newman.helpers import (
    NewmanTestCase,
    DateTimeAssert,
)

class TestArticle(NewmanTestCase):
    translation_language_code = 'cs'
    make_translation = True

    def test_recycle_article(self):
        STEP_SLEEP = 2
        s = self.selenium
        self.test_create_article()
        s.wait_for_element_present('save-form')
        s.click(self.elements['controls']['save_draft'])
        s.wait_for_element_present('popup_prompt')
        s.type('popup_prompt', 'Recyclation preset')
        s.click(self.elements['controls']['popup_ok'])
        s.wait_for_element_present(self.elements['controls']['message_bubble'])# wait until the preset is saved
        sleep(STEP_SLEEP)
        s.click(self.elements['navigation']['article_add'])
        when_created = strftime('%y-%m-%d %H:%M')
        s.wait_for_element_present(self.elements['controls']['message_bubble']) # wait until the form is loaded, then load 'Recyclation preset'
        sleep(STEP_SLEEP)
        # focus combobox and type preset name (to select it)
        s.select(
            self.elements['controls']['combobox_drafts'], 
            'label=Recyclation preset (%s)' % when_created
        )
        sleep(STEP_SLEEP)
        
        data = {
            'title' : u'From preset 马 žš experiment',
            'slug' : u'from-preset-zs-experiment',
        }
        self.fill_fields(data)
        # verify all fields
        expected_data = {
            'title' : u'From preset 马 žš experiment',
            'slug' : u'from-preset-zs-experiment',
            'category' : [u"Africa/west-africa"],
            'authors' : [u"Barack Obama", u"King Albert II"],
            'upper_title' : u'vyšší',
            'description' : u'Article description',
            'placement_set-0-category' : [u"Africa/west-africa"],
            'tagging-taggeditem-content_type-object_id-0-tag': '1#Music',
            'tagging-taggeditem-content_type-object_id-0-id': '', #before save should be empty
            'tagging-taggeditem-content_type-object_id-1-tag': '2#Moovie',
            'tagging-taggeditem-content_type-object_id-1-id': '', #before save should be empty
        }
        self.verify_form(expected_data)

        self.save_form()
        self.assert_equals(expected_data['title'], s.get_text(self.get_listing_object_href()))
        s.click(self.get_listing_object_href())
        expected_data.update({
            'tagging-taggeditem-content_type-object_id-0-id': '3', #now should be set
            'tagging-taggeditem-content_type-object_id-1-id': '4', #now should be set
            'tagging-taggeditem-content_type-object_id-2-id': '',
        })
        self.verify_form(expected_data)

    def test_create_article(self):
        s = self.selenium

        # go to article adding
        s.click(self.elements['navigation']['articles'])
        s.wait_for_element_present(self.elements['controls']['add'])
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
            'placement_set-0-category' : ('we',),
            # fill tags
            'tagging-taggeditem-content_type-object_id-0-tag' : ('Musi',), 
            'tagging-taggeditem-content_type-object_id-1-tag' : ('Moov',),
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
        
        # fill exports
        export_inline_suggest_data = {
            'exportmeta_set-0-export' : ('Example Export',),
        }
        self.fill_suggest_fields(export_inline_suggest_data) # fill exportinline suggest fields when placement inline is completely filled.

        # TODO: Replace fuzzy matching when it will be decided how to insert time
        expected_data.update({
            "placement_set-0-publish_from" : DateTimeAssert(datetime(
                year = int(strftime("%Y")),
                month = int(strftime("%m")),
                day = int(calendar_data['publish_from']['day']),
                hour = 0,
                minute = 0,
            )),

            "placement_set-0-publish_to" : DateTimeAssert(datetime(
                year = int(strftime("%Y")),
                month = int(strftime("%m")),
                day = int(calendar_data['publish_to']['day']),
                hour = 0,
                minute = 0,
            )),
        })

        self.save_form()

        s.wait_for_element_present(self.get_listing_object()+"/th")

        self.assert_equals(data['title'], s.get_text(self.get_listing_object_href()))

        # verify all fields
        s.click(self.get_listing_object_href())

        self.verify_form(expected_data)

    def test_article_search_from_articles(self):
        s = self.selenium
        search_term = 'experiment'
        search_input = "//input[@id='searchbar']"

        # go to articles
        s.click(self.elements['navigation']['articles'])
        s.wait_for_element_present(search_input)

        # write search term
        s.type('searchbar', search_term)
        s.click(self.elements['controls']['search_button'])

        # check that search input contains search term and we have 1 article
        s.wait_for_element_present(search_input)
        self.assert_equals(s.get_value("searchbar"), search_term)

