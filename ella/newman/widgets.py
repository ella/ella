from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.db.models.fields.related import ForeignKey
from django.contrib.admin import widgets
from django.utils.text import truncate_words
from ella.ellaadmin.utils import admin_url

JS_EDITOR = 'js/editor.js'
JS_SHOWDOWN = 'js/showdown.js'
CLASS_RICHTEXTAREA = 'rich_text_area'
CSS_RICHTEXTAREA = 'css/editor.css'

# Generic suggester media files
JS_GENERIC_SUGGEST = 'js/generic.suggest.js'
CSS_GENERIC_SUGGEST = 'css/generic.suggest.css'

# Fake windows
JS_JQUERY_UI = 'js/jquery-ui.js'


class ForeignKeyRawIdWidget(widgets.ForeignKeyRawIdWidget):
    def label_for_value(self, value):
        obj = self.rel.to.objects.get(pk=value)
        label = truncate_words(obj, 14)
        adm = admin_url(obj)
        return '&nbsp;<a href="%s">%s</a>' % (adm, label)


class RichTextAreaWidget(forms.Textarea):
    'Widget representing the RichTextEditor.'
    class Media:
        js = (
            settings.NEWMAN_MEDIA_PREFIX + JS_EDITOR,
            settings.NEWMAN_MEDIA_PREFIX + JS_SHOWDOWN,
        )
        css = {
            'screen': (settings.ADMIN_MEDIA_PREFIX + CSS_RICHTEXTAREA,),
        }
    def __init__(self, height=None, attrs={}):
        css_class = CLASS_RICHTEXTAREA
        if height:
            css_class += ' %s' % height
        super(RichTextAreaWidget, self).__init__(attrs={'class': css_class})


class AdminSuggestWidget(forms.TextInput):
    class Media:
        js = (settings.NEWMAN_MEDIA_PREFIX + JS_JQUERY_UI, settings.NEWMAN_MEDIA_PREFIX + JS_GENERIC_SUGGEST,)
        css = {'screen': (settings.NEWMAN_MEDIA_PREFIX + CSS_GENERIC_SUGGEST,),}

    def __init__(self, db_field, attrs={}, **kwargs):
        self.db_field = db_field
        self.ownmodel = kwargs.pop('model')
        self.lookups = kwargs.pop('lookup')
        self.model = self.db_field.rel.to
        self.is_hidden = True

        super(AdminSuggestWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):

        # related_url for standard lookup and clreate suggest_url for JS suggest
        related_url = '../../../%s/%s/' % (self.model._meta.app_label, self.model._meta.object_name.lower())
        suggest_params = '&amp;'.join([ 'f=%s' % l for l in self.lookups ]) + '&amp;q='
        suggest_url = related_url + 'suggest/?' + suggest_params

        if self.db_field.rel.limit_choices_to:
            url = '?' + '&amp;'.join(['%s=%s' % (k, v) for k, v in self.db_field.rel.limit_choices_to.items()])
        else:
            url = ''


        if isinstance(self.db_field, ForeignKey):
            attrs['class'] = 'vForeignKeyRawIdAdminField hidden'
            suggest_css_class = 'GenericSuggestField'
        else:
            attrs['class'] = 'vManyToManyRawIdAdminField hidden'
            suggest_css_class = 'GenericSuggestFieldMultiple'

        if not value:
            suggest_items = ''
        else:
            try:
                if isinstance(self.db_field, ForeignKey):
                    suggest_items = '<li class="suggest-selected-item">%s <a class="suggest-delete-link">x</a></li>' % getattr(self.model.objects.get(pk=value), self.lookups[0])
                else:
                    if not isinstance(value, (list, tuple)):
                        value = [int(v) for v in value.split(',')]
                    suggest_items = ''.join('<li class="suggest-selected-item">%s <a class="suggest-delete-link">x</a></li>' % \
                                             getattr(i, self.lookups[0]) for i in self.model.objects.filter(pk__in=value))
                    value = ','.join(["%s" % v for v in value])
            except self.model.DoesNotExist:
                suggest_items = ''


        output = [super(AdminSuggestWidget, self).render(name, value, attrs)]

        output.append('<ul class="%s">%s<li><input type="text" id="id_%s_suggest" rel="%s" /></li></ul> ' \
                      % (suggest_css_class, suggest_items, name, suggest_url))
        # TODO: "id_" is hard-coded here. This should instead use the correct
        # API to determine the ID dynamically.
        output.append('<a href="%s%s" class="suggest-related-lookup" id="lookup_id_%s" onclick="return showRelatedObjectLookupPopup(this);"> ' % \
            (related_url, url, name))
        output.append('<img src="%simg/admin/selector-search.gif" width="16" height="16" alt="Lookup" /></a>' % settings.ADMIN_MEDIA_PREFIX)
        return mark_safe(u''.join(output))
