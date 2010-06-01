# -*- coding: utf-8 -*-
from copy import copy
from datetime import datetime
from time import strftime, sleep

from django.utils.translation import ugettext_lazy as _

from ella.polls.models import Survey

from example_project.tests.test_newman.helpers import (
    NewmanTestCase,
    DateTimeAssert,
)

class TestSurvey(NewmanTestCase):
    translation_language_code = 'cs'
    make_translation = True

    def test_recycle_survey(self):
        STEP_SLEEP = 2
        s = self.selenium
        self.test_create_survey()
        s.wait_for_element_present('save-form')
        s.click(self.elements['controls']['save_draft'])
        s.wait_for_element_present('popup_prompt')
        s.type('popup_prompt', 'Recyclation preset')
        s.click(self.elements['controls']['popup_ok'])
        s.wait_for_element_present(self.elements['controls']['message_bubble'])# wait until the preset is saved
        sleep(STEP_SLEEP)

        s.click(self.elements['navigation']['survey_add'])
        when_created = strftime('%y-%m-%d %H:%M')
        s.wait_for_element_present(self.elements['controls']['message_bubble']) # wait until the form is loaded, then load 'Recyclation preset'
        sleep(STEP_SLEEP)
        # focus combobox and type preset name (to select it)
        s.select(
            self.elements['controls']['combobox_drafts'], 
            'label=Recyclation preset (%s)' % when_created
        )
        sleep(STEP_SLEEP)

        # fill the form
        active_from = '%s%02d 00:00' % (strftime('%Y-%m-'), 1)
        active_to = '%s%02d 00:00' % (strftime('%Y-%m-'), 10)
        data = {
            'question' : u'Recycled -- 马 žš experiment',
        }
        self.fill_fields(data)
        expected_data = copy(data)
        # check filled data in
        expected_data.update({
            'choice_set-0-choice': u'Choice #1\n马 žš experiment',
            'choice_set-1-choice': u'Choice #2\n马 žš experiment',
            'choice_set-2-choice': u'Choice #3\n马 žš experiment',
            'active_from': active_from,
            'active_till': active_to,
        })
        self.verify_form(expected_data)

        self.save_form()
        s.wait_for_element_present(self.get_listing_object()+"/th")
        self.assert_equals(data['question'], s.get_text(self.get_listing_object_href(position=2, a_element_position=1)))
        # verify all fields
        s.click(self.get_listing_object_href(position=2, a_element_position=1))
        self.verify_form(expected_data)

    def test_create_survey(self):
        s = self.selenium
        # go to article adding
        s.click(self.elements['navigation']['surveys'])
        s.wait_for_element_present(self.elements['controls']['add'])
        s.click(self.elements['controls']['add'])

        s.wait_for_element_present("//textarea[@id='id_choice_set-2-choice']")

        # fill the form
        data = {
            'question' : u'马 žš experiment',
            'choice_set-0-choice': u'Choice #1\n马 žš experiment',
            'choice_set-1-choice': u'Choice #2\n马 žš experiment',
            'choice_set-2-choice': u'Choice #3\n马 žš experiment',
        }
        self.fill_fields(data)
        expected_data = copy(data)

        active_from = '%s%02d 00:00' % (strftime('%Y-%m-'), 1)
        active_to = '%s%02d 00:00' % (strftime('%Y-%m-'), 10)
        expected_data.update({
            'active_from': active_from,
            'active_till': active_to,
        })
        self.fill_calendar_field('active_from', 1) # form row contains class 'active_from'
        self.fill_calendar_field('active_till', 10)

        self.save_form()
        s.wait_for_element_present(self.get_listing_object()+"/th")
        self.assert_equals(data['question'], s.get_text(self.get_listing_object_href(a_element_position=1)))
        # verify all fields
        s.click(self.get_listing_object_href(a_element_position=1))
        self.verify_form(expected_data)

    def fill_calendar_field(self, calendar_field_class, day):
        s = self.selenium
        # click on calendar
        xpath = "//div[contains(@class,'%s')]/div[@class='form-row-field']/span[@class='js-dtpicker-trigger']" % calendar_field_class
        s.click(xpath)

        day_xpath = self.elements['pages']['listing']['calendar_day'] % {
            'day' : day
        }
        s.click(day_xpath)
