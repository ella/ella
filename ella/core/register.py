from django import forms
from django.utils.translation import ugettext_lazy as _

from app_data import app_registry, AppDataForm, AppDataContainer

from ella.core.models import Category
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

app_registry.register('ella', AppDataContainer.from_form(CategoryAppForm), Category)

