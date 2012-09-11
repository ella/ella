from django import forms

from app_data import app_registry, AppDataForm, AppDataContainer

from ella.core.models import Category
from ella.core.conf import core_settings

class CategoryAppForm(AppDataForm):
    archive_template = forms.CharField(initial=core_settings.ARCHIVE_TEMPLATE, required=False)
    no_home_listings = forms.BooleanField(initial=core_settings.CATEGORY_NO_HOME_LISTINGS, required=False)
    listing_handler = forms.CharField(initial='default', required=False)
    paginate_by = forms.IntegerField(initial=core_settings.CATEGORY_LISTINGS_PAGINATE_BY, required=False)
    propagate_listings = forms.BooleanField(initial=True, required=False)

app_registry.register('ella', AppDataContainer.from_form(CategoryAppForm), Category)

