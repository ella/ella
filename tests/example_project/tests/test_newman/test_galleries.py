# -*- coding: utf-8 -*-
from copy import copy
from django.utils.translation import ugettext_lazy as _

from ella.galleries.models import Gallery

from time import strftime, sleep
from example_project.tests.test_newman.helpers import NewmanTestCase

# Linux   Firefox 3.6.x fails tests 3, 5, 9.
# Windows Firefox 3.6.x fails tests 5, 9.

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
    11. Recycle gallery. (Make preset from existing gallery, create new gallery from the preset. Save gallery.)
    """
    def test_recycle_gallery(self):
        STEP_SLEEP = 2
        s = self.selenium
        self.test_create_gallery()
        s.wait_for_element_present('save-form')
        s.click(self.elements['controls']['save_draft'])
        s.wait_for_element_present('popup_prompt')
        s.type('popup_prompt', 'Recyclation preset')
        s.click(self.elements['controls']['popup_ok'])
        s.wait_for_element_present(self.elements['controls']['message_bubble'])# wait until the preset is saved
        sleep(STEP_SLEEP)
        s.click(self.elements['navigation']['gallery_add'])
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
            'slug': u'from-preset-zs-experiment'
        }
        self.fill_fields(data)
        # verify all fields
        expected_data = {
            'category' : [u"Africa/west-africa"],
            'authors' : [u"Barack Obama", u"King Albert II"],
            'title' : u'From preset 马 žš experiment',
            'description' : u'Gallery description',
            'content' : u'šialený obsah galörie',
            'slug': u'from-preset-zs-experiment',
            'galleryitem_set-0-target_id': '1',
            'galleryitem_set-1-target_id': '2',
            'galleryitem_set-2-target_id': '3',
            'galleryitem_set-3-target_id': '4',
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
            'tagging-taggeditem-content_type-object_id-2-id': '', #now should be set
        })
        self.verify_form(expected_data)

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
        # create placement
        s.click(self.elements['controls']['placement_default_category_button'])
        s.type('id_placement_set-0-publish_from', strftime('%Y-%m-%d %H:%M'))
        # fill tags
        suggest_data = {
            'tagging-taggeditem-content_type-object_id-0-tag' : ('Musi',),
            'tagging-taggeditem-content_type-object_id-1-tag' : ('Moov',),
        }
        self.fill_suggest_fields(suggest_data)

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
