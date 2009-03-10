from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import CheckboxSelectMultiple

from ella.core.models import Category
from ella.newman.models import DenormalizedCategoryUserRole

class SiteFilterForm(forms.Form):

    def __init__(self, data=None, user=None, **kwargs):
        super(SiteFilterForm, self).__init__(data=data, **kwargs)
        self.init_form(user)

    def init_form(self, user):
        category_ids = DenormalizedCategoryUserRole.objects.root_categories_by_user(user)
        cats = Category.objects.filter(pk__in=category_ids)
        choices = ()
        for c in cats:
            choices += (c.pk, c.__unicode__(),),
        self.fields['sites'] = forms.MultipleChoiceField(choices, widget=CheckboxSelectMultiple)

