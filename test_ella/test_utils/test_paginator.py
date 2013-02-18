from unittest import TestCase

from nose import tools
from ella.utils.pagination import FirstPagePaginator


OBJECTS = ['1', '2', '3', '4', '5']


class TestPaginator(TestCase):
    def test_diffrerent_first_page(self):
        p = FirstPagePaginator(OBJECTS, first_page_count=1, per_page=2)

        tools.assert_equals(p.page(1).object_list, ['1'])

    def test_other_pages(self):
        p = FirstPagePaginator(OBJECTS, first_page_count=1, per_page=2)

        tools.assert_equals(p.page(2).object_list, ['2', '3'])
        tools.assert_equals(p.page(3).object_list, ['4', '5'])

    def test_all_pages_same(self):
        p = FirstPagePaginator(OBJECTS, per_page=2)

        tools.assert_equals(p.page(1).object_list, ['1', '2'])
        tools.assert_equals(p.page(2).object_list, ['3', '4'])
