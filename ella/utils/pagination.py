from math import ceil

from django.core.paginator import Paginator, Page


class FirstPagePaginator(Paginator):
    """
    Extends standard django paginator by possibility of having different
    number of items on the first page.
    """
    def __init__(self, object_list, per_page, orphans=0,
                 allow_empty_first_page=True, first_page_count=None):
        super(FirstPagePaginator, self).__init__(object_list, per_page,
                                                 orphans,
                                                 allow_empty_first_page)
        self.first_page_count = first_page_count or per_page

    def page(self, number):
        number = self.validate_number(number)
        bottom = (number - 2) * self.per_page + self.first_page_count if number > 1 else 0
        top = bottom + (self.first_page_count if number == 1 else self.per_page)
        if top + self.orphans >= self.count:
            top = self.count
        return Page(self.object_list[bottom:top], number, self)

    def _get_num_pages(self):
        if self._num_pages is None:
            if self.count == 0 and not self.allow_empty_first_page:
                self._num_pages = 0
            else:
                hits = max(1, self.count - self.first_page_count - self.orphans)
                self._num_pages = (int(ceil(hits / float(self.per_page))) + 1
                                        if self.count > self.first_page_count
                                        else 1)
        return self._num_pages

    num_pages = property(_get_num_pages)
