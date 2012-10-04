from django import forms
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator

from app_data import app_registry, AppDataForm, AppDataContainer

from ella.core.models import Category, Listing
from ella.core.conf import core_settings

class CategoryAppForm(AppDataForm):
    archive_template = forms.CharField(initial=core_settings.ARCHIVE_TEMPLATE, required=False)
    no_home_listings = forms.BooleanField(initial=core_settings.CATEGORY_NO_HOME_LISTINGS, required=False)
    listing_handler = forms.CharField(initial='default', required=False)
    paginate_by = forms.IntegerField(label=_('Paginate by'),
        initial=core_settings.CATEGORY_LISTINGS_PAGINATE_BY, required=False,
        help_text=_('How many records to show on one listing page.'))
    propagate_listings = forms.BooleanField(label=_('Propagate listings'),
        initial=True, required=False, help_text=_('Should propagate listings '
        'from child categories?'))

class EllaAppDataContainer(AppDataContainer):
    form_class = CategoryAppForm

    def get_listings(self, **kwargs):
        return Listing.objects.get_queryset_wrapper(self._instance, **kwargs)

    def get_listings_page(self, page_no, **kwargs):
        paginate_by = self.paginate_by
        paginator = Paginator(self.get_listings, paginate_by)

        if page_no > paginator.num_pages or page_no < 1:
            raise Http404(_('Invalid page number %r') % page_no)

        return paginator.page(page_no)


app_registry.register('ella', EllaAppDataContainer, Category)

