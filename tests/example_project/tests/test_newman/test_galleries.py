# -*- coding: utf-8 -*-
from copy import copy
from django.utils.translation import ugettext_lazy as _

from ella.galleries.models import Gallery

from time import strftime, sleep
from example_project.tests.test_newman.helpers import NewmanTestCase

DRAG_SLEEP = 0.5 #in sec.
class TestGallery(NewmanTestCase):
    """
    TODO:
    1. Vytvoreni nove galerie s nekolika prvky. Ulozit.
    2. Bod 1 bez ulozeni + zkusit smazat nektere prvky. Ulozit.
    3. Bod 2 bez ulozeni + pridat misto nich nejake jine prvky. Ulozit.
    4. Otevrit existujici galerii. Upravit perex. Ulozit.
    5. Otevrit existujici galerii. Upravit poradi fotek. Ulozit.
    6. Otevrit existujici galerii. Pridat fotku. Ulozit.
    7. Otevrit existujici galerii. Smazat fotku. Ulozit.
    8. Otevrit existujici galerii. Vymenit fotky. Ulozit.
    9. Otevrit existujici galerii. Vymenit fotky, zmenit jejich poradi. Ulozit.
    10. Otevrit existujici galerii. Pridat fotku. Pridanou fotku smazat (mela by zmizet okamzite po kliknuti). Ulozit.
    """

    def test_change_photos_swap_them_and_save(self):
        " This method covers point 9 from TODO section on top of this class. "
        s = self.selenium
        self.test_create_gallery()

        expected_data = {
            'category' : [u"Africa/west-africa"],
            'authors' : [u"Barack Obama", u"King Albert II"],
            'title' : u'马 žš experiment',
            'description' : u'Gallery description',
            'content' : u'šialený obsah galörie',
            'slug' : u'experiment',
            'galleryitem_set-0-target_id': '1',
            'galleryitem_set-1-target_id': '6',
            'galleryitem_set-2-target_id': '5',
            'galleryitem_set-3-target_id': '3',
        }
        self.add_photo_to_position(1, 'Fifth Example')
        self.add_photo_to_position(3, 'Sixth Example')

        # swap any two gallery items
        #drag 'n' drop item at position 3 to position 1
        drag_item = self.elements['pages']['gallery']['item'] % \
            {'id': 'lookup_id_galleryitem_set-3-target_id'}
        drop_above_item = self.elements['pages']['gallery']['item'] % \
            {'id': 'lookup_id_galleryitem_set-1-target_id'}
        expected_data_before_save = {
            'galleryitem_set-1-order': '3000',
            'galleryitem_set-3-order': '2000',
        }
        s.mouse_down_at(drag_item, '10,10')
        sleep(DRAG_SLEEP)
        s.mouse_move_at(drop_above_item, '10,10')
        sleep(DRAG_SLEEP)
        s.mouse_over(drop_above_item)
        sleep(DRAG_SLEEP)
        s.mouse_up_at(drop_above_item, '10,10')
        sleep(DRAG_SLEEP)
        self.verify_form(expected_data_before_save)

        self.save_form()
        self.assert_equals(expected_data['title'], s.get_text(self.get_listing_object_href()))
        # verify all fields
        s.click(self.get_listing_object_href())
        self.verify_form(expected_data)

    def test_change_photos_and_save(self):
        " This method covers point 8 from TODO section on top of this class. "
        s = self.selenium
        self.test_create_gallery()

        expected_data = {
            'category' : [u"Africa/west-africa"],
            'authors' : [u"Barack Obama", u"King Albert II"],
            'title' : u'马 žš experiment',
            'description' : u'Gallery description',
            'content' : u'šialený obsah galörie',
            'slug' : u'experiment',
            'galleryitem_set-0-target_id': '1',
            'galleryitem_set-1-target_id': '5',
            'galleryitem_set-2-target_id': '3',
            'galleryitem_set-3-target_id': '6',
        }
        self.add_photo_to_position(1, 'Fifth Example')
        self.add_photo_to_position(3, 'Sixth Example')

        self.save_form()
        self.assert_equals(expected_data['title'], s.get_text(self.get_listing_object_href()))
        # verify all fields
        s.click(self.get_listing_object_href())
        self.verify_form(expected_data)

    def test_delete_photo_in_existing_gallery_and_save(self):
        " This method covers point 7 from TODO section on top of this class. "
        s = self.selenium
        self.test_create_gallery()

        expected_data = {
            'category' : [u"Africa/west-africa"],
            'authors' : [u"Barack Obama", u"King Albert II"],
            'title' : u'马 žš experiment',
            'description' : u'Gallery description',
            'content' : u'šialený obsah galörie',
            'slug' : u'experiment',
            'galleryitem_set-0-target_id': '1',
            'galleryitem_set-1-target_id': '2',
            'galleryitem_set-2-target_id': '3',
            'galleryitem_set-3-target_id': '', # deleted item
        }
        self.click_item_delete(3)

        self.save_form()
        self.assert_equals(expected_data['title'], s.get_text(self.get_listing_object_href()))
        # verify all fields
        s.click(self.get_listing_object_href())
        self.verify_form(expected_data)

    def test_adding_photo_to_existing_galery_and_save(self):
        " This method covers point 6 from TODO section on top of this class. "
        s = self.selenium
        self.test_create_gallery()

        expected_data = {
            'category' : [u"Africa/west-africa"],
            'authors' : [u"Barack Obama", u"King Albert II"],
            'title' : u'马 žš experiment',
            'description' : u'Gallery description',
            'content' : u'šialený obsah galörie',
            'slug' : u'experiment',
            'galleryitem_set-0-target_id': '1',
            'galleryitem_set-1-target_id': '2',
            'galleryitem_set-2-target_id': '3',
            'galleryitem_set-3-target_id': '4',
            'galleryitem_set-4-target_id': '5',
        }
        self.add_photo_to_position(4, 'Fifth Example')

        self.save_form()
        self.assert_equals(expected_data['title'], s.get_text(self.get_listing_object_href()))
        # verify all fields
        s.click(self.get_listing_object_href())
        self.verify_form(expected_data)

    def test_item_ordering_changed(self):
        " This method covers point 5 from TODO section on top of this class. "
        s = self.selenium
        self.test_create_gallery()
        expected_data = {
            'category' : [u"Africa/west-africa"],
            'authors' : [u"Barack Obama", u"King Albert II"],
            'title' : u'马 žš experiment',
            'description' : u'Gallery description',
            'content' : u'šialený obsah galörie',
            'slug' : u'experiment',
            'galleryitem_set-0-target_id': '1',
            'galleryitem_set-1-target_id': '3', #at position 2
            'galleryitem_set-2-target_id': '2', #at position 1
            'galleryitem_set-3-target_id': '4',
            'galleryitem_set-1-order': '2',
            'galleryitem_set-2-order': '3',
        }
        #drag 'n' drop item at position 2 to position 1
        drag_item = self.elements['pages']['gallery']['item'] % \
            {'id': 'lookup_id_galleryitem_set-2-target_id'}
        drop_above_item = self.elements['pages']['gallery']['item'] % \
            {'id': 'lookup_id_galleryitem_set-1-target_id'}
        expected_data_before_save = {
            'galleryitem_set-1-order': '3000',
            'galleryitem_set-2-order': '2000',
        }
        s.mouse_down_at(drag_item, '10,10')
        sleep(DRAG_SLEEP)
        s.mouse_move_at(drop_above_item, '10,10')
        sleep(DRAG_SLEEP)
        s.mouse_over(drop_above_item)
        sleep(DRAG_SLEEP)
        s.mouse_up_at(drop_above_item, '10,10')
        sleep(DRAG_SLEEP)
        self.verify_form(expected_data_before_save)

        self.save_form()
        self.assert_equals(expected_data['title'], s.get_text(self.get_listing_object_href()))
        # verify all fields
        s.click(self.get_listing_object_href())
        self.verify_form(expected_data)

    def test_perex_changed(self):
        " This method covers point 4 from TODO section on top of this class. "
        s = self.selenium
        self.test_create_gallery()
        data = {
            'description' : u'Gallery description changed.',
        }
        expected_data = {
            'category' : [u"Africa/west-africa"],
            'authors' : [u"Barack Obama", u"King Albert II"],
            'title' : u'马 žš experiment',
            'description' : u'Gallery description changed.',
            'content' : u'šialený obsah galörie',
            'slug' : u'experiment',
            'galleryitem_set-0-target_id': '1',
            'galleryitem_set-1-target_id': '2',
            'galleryitem_set-2-target_id': '3',
            'galleryitem_set-3-target_id': '4',
        }
        self.fill_fields(data)

        self.save_form()
        self.assert_equals(expected_data['title'], s.get_text(self.get_listing_object_href()))
        # verify all fields
        s.click(self.get_listing_object_href())
        self.verify_form(expected_data)

    def test_fill_new_gallery_delete_several_items_then_add_another_items_and_save(self):
        " This method covers point 3 from TODO section on top of this class. "
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
        # add four photos
        self.add_photos()
        # remove second photo
        self.click_item_delete(1)
        expected_data.update({
            'category' : [u"Africa/west-africa"],
            'authors' : [u"Barack Obama", u"King Albert II"],
            'title' : u'马 žš experiment',
            'description' : u'Gallery description',
            'content' : u'šialený obsah galörie',
            'slug' : u'experiment',
            'galleryitem_set-0-target_id': '1',
            # Second item is deleted.
            'galleryitem_set-1-target_id': '3',
            'galleryitem_set-2-target_id': '4',
        })

        # add another two photos
        self.add_photo_to_position(3, 'Fifth Example')
        self.add_photo_to_position(4, 'Sixth Example')
        expected_data.update({
            'galleryitem_set-3-target_id': '5',
            'galleryitem_set-4-target_id': '6',
        })

        self.save_form()
        self.assert_equals(data['title'], s.get_text(self.get_listing_object_href()))

        # verify all fields
        s.click(self.get_listing_object_href())
        self.verify_form(expected_data)

    def test_fill_new_gallery_delete_several_items_and_save(self):
        " This method covers point 2 from TODO section on top of this class. "
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
        # add four photos
        self.add_photos()
        # remove second photo
        self.click_item_delete(1)

        expected_data.update({
            'category' : [u"Africa/west-africa"],
            'authors' : [u"Barack Obama", u"King Albert II"],
            'title' : u'马 žš experiment',
            'description' : u'Gallery description',
            'content' : u'šialený obsah galörie',
            'slug' : u'experiment',
            'galleryitem_set-0-target_id': '1',
            # Second item is deleted.
            'galleryitem_set-1-target_id': '3',
            'galleryitem_set-2-target_id': '4',
        })
        self.save_form()
        self.assert_equals(data['title'], s.get_text(self.get_listing_object_href()))

        # verify all fields
        s.click(self.get_listing_object_href())
        self.verify_form(expected_data)

    def test_open_gallery_add_photo_and_remove_photo_and_save(self):
        " This method covers point 10 from TODO section on top of this class. "
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
        # add two photos
        self.add_two_photos()
        # save it 
        self.save_form()
        self.assert_equals(data['title'], s.get_text(self.get_listing_object_href()))

        # open existing gallery object
        s.click(self.get_listing_object_href())

        # add and remove third photo
        self.add_third_photo()
        self.click_item_delete(2)

        expected_data.update({
            'category' : [u"Africa/west-africa"],
            'authors' : [u"Barack Obama", u"King Albert II"],
            'title' : u'马 žš experiment',
            'description' : u'Gallery description',
            'content' : u'šialený obsah galörie',
            'slug' : u'experiment',
            'galleryitem_set-0-target_id': '1',
            'galleryitem_set-1-target_id': '2',
        })
        # save it 
        self.save_form()
        self.assert_equals(data['title'], s.get_text(self.get_listing_object_href()))

        # verify all fields
        s.click(self.get_listing_object_href())
        self.verify_form(expected_data)

    def test_create_gallery(self):
        " This method covers point 1 from TODO section on top of this class. "
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
        # add four photos
        self.add_photos()

        expected_data.update({
            'category' : [u"Africa/west-africa"],
            'authors' : [u"Barack Obama", u"King Albert II"],
            'title' : u'马 žš experiment',
            'description' : u'Gallery description',
            'content' : u'šialený obsah galörie',
            'slug' : u'experiment',
            'galleryitem_set-0-target_id': '1',
            'galleryitem_set-1-target_id': '2',
            'galleryitem_set-2-target_id': '3',
            'galleryitem_set-3-target_id': '4',
        })
        self.save_form()
        self.assert_equals(data['title'], s.get_text(self.get_listing_object_href()))

        # verify all fields
        s.click(self.get_listing_object_href())
        self.verify_form(expected_data)

    def click_item(self, no):
        sel = self.selenium
        item_id = 'lookup_id_galleryitem_set-%d-target_id' % no
        # display overlay (click to the lupicka)
        first_item = self.elements['pages']['gallery']['item'] % \
            {'id': item_id}
        sel.click(first_item)

    def click_item_delete(self, no):
        sel = self.selenium
        item_id = 'id_galleryitem_set-%d-DELETE' % no
        # display overlay (click to the lupicka)
        first_item = self.elements['pages']['gallery']['item_input'] % \
            {'id': item_id}
        sel.click(first_item)

    def add_photo_to_position(self, position, photo_name):
        sel = self.selenium
        self.click_item(position)
        sel.wait_for_element_present('overlay-content-main')
        overlay = self.elements['controls']['overlay']
        photo = "%s/descendant::*/a[text()='%s']" % (overlay, photo_name)
        sel.click(photo)

    def add_two_photos(self):
        self.add_photo_to_position(0, 'First Example')
        self.add_photo_to_position(1, 'Second Example')

    def add_third_photo(self):
        self.add_photo_to_position(2, 'Third Example')

    def add_photos(self):
        sel = self.selenium

        self.add_two_photos()
        self.add_third_photo()

        self.add_photo_to_position(3, 'Fourth Example')
