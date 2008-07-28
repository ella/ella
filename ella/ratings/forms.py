from django import forms
from ella.core.cache import get_cached_object
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.db import models

CONTENT_TYPE_CT = ContentType.objects.get_for_model(ContentType)
class RateForm(forms.Form):
    content_type = forms.IntegerField(widget=forms.HiddenInput)
    target = forms.IntegerField(widget=forms.HiddenInput)

    def clean_content_type(self):
        try:
            value = get_cached_object(CONTENT_TYPE_CT, pk=self.cleaned_data['content_type'])
        except models.ObjectDoesNotExist:
            raise forms.ValidationError, _('The given ContentType object does not exist.')
        return value

    def clean_target(self):
        try:
            value = get_cached_object(self.cleaned_data['content_type'], pk=self.cleaned_data['target'])
        except models.ObjectDoesNotExist:
            raise forms.ValidationError, _('The given target object does not exist.')
        return value

