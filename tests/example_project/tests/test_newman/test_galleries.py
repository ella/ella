# -*- coding: utf-8 -*-
from copy import copy
from django.utils.translation import ugettext_lazy as _

from ella.galleries.models import Gallery

from time import strftime
from example_project.tests.test_newman.helpers import NewmanTestCase

class TestGallery(NewmanTestCase):

    def test_gallery_saving(self):
        s = self.selenium

        s.click(self.elements['navigation']['galleries'])
        s.click(self.elements['controls']['add'])
        
        s.wait_for_element_present('id_content')
        data = {
            'title' : u'马 žš experiment',
            'description' : u'Gallery description',
            'content' : u'šialený obsah galörie',
            'slug' : u'experiment',
        }
        self.fill_fields(data)

        expected_data = copy(data)
        
        suggest_data = {
            'category': ('we',),
            'authors':  ('Bar', 'Kin',),
        }
        self.fill_suggest_fields(suggest_data)
        
        expected_data.update({
            'category' : [u"Africa/west-africa"],
            'authors' : [u"Barack Obama", u"King Albert II"],
        })

        self.save_form()
        self.assert_equals(u"%s: %s" % (unicode(_(u"Gallery")), data['title']), s.get_text(self.get_listing_object_href()))

        # verify all fields
        s.click(self.get_listing_object()+"/th/a[@class='hashadr']")
        self.verify_form(expected_data)

