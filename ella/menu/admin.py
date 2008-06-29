from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.newforms.widgets import *
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django import newforms as forms
from django.newforms import ModelForm

from ella.core.cache.utils import delete_cached_object
from ella.ellaadmin import widgets
from ella.ellaadmin.options import EllaAdminSite
from ella.menu.models import MenuItem, Menu

class MenuItemForm(ModelForm):
    def clean(self):
        # TODO testovat, pokud menuitem obsahuje podpolozky, musi mit akorat label, netreba url ni target
        data = self.cleaned_data
        if data['url'] or (data['target_id'] and data['target_ct']):
            if data['url']:
                pass # use URL
            else:
                pass # use generic relation
        elif not data['url'] and not data['target_id'] and not data['target_ct']:
            raise forms.ValidationError(_('Please specify either URL or target_id and contentype fields.'))
        return data

class MenuItemOptions(admin.ModelAdmin):
    form = MenuItemForm
    search_fields = ('label', 'menu', 'url')

admin.site.register(Menu)
admin.site.register(MenuItem, MenuItemOptions)

