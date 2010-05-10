# -*- coding: utf-8 -*-
from copy import copy
from django.utils.translation import ugettext_lazy as _

from ella.galleries.models import Gallery

from time import strftime, sleep
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

        self.add_photos()

        expected_data.update({
            'category' : [u"Africa/west-africa"],
            'authors' : [u"Barack Obama", u"King Albert II"],
        })

        self.save_form()
        self.assert_equals(data['title'], s.get_text(self.get_listing_object_href()))

        # verify all fields
        s.click(self.get_listing_object_href())
        self.verify_form(expected_data)

    def add_photos(self):
        sel = self.selenium
        # display overlay (click to the lupicka)
        first_item = self.elements['pages']['gallery']['item'] % \
            {'id': 'lookup_id_galleryitem_set-0-target_id'}
        sel.click(first_item)

        # select first item, add it to the gallery items
        sel.wait_for_element_present('overlay-content-main')
        overlay = self.elements['controls']['overlay']
        first_photo = "%s/descendant::*/a[text()='First Example']" % overlay
        sel.click(first_photo)
        pass

    def todo(self):
        """
        1. Vytvoreni nove galerie s nekolika prvky. Ulozit.
        2. Bod 1 + zkusit smazat nektere prvky. Ulozit.
        3. Bod 2 + pridat misto nich nejake jine prvky. Ulozit.
        4. Otevrit existujici galerii. Upravit perex. Ulozit.
        5. Otevrit existujici galerii. Upravit poradi fotek. Ulozit.
        6. Otevrit existujici galerii. Pridat fotku. Ulozit.
        7. Otevrit existujici galerii. Smazat fotku. Ulozit.
        8. Otevrit existujici galerii. Vymenit fotky. Ulozit.
        9. Otevrit existujici galerii. Vymenit fotky, zmenit jejich poradi. Ulozit.
        """
