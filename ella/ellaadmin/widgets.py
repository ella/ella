from django import forms
from django.conf import settings
from django.contrib.admin import widgets
from django.utils.safestring import mark_safe
from django.utils.text import truncate_words
from django.template import Context
from django.template.loader import get_template

from ella.ellaadmin.utils import admin_url
from ella.core.models import Listing


JS_EDITOR = 'js/editor.js'
JS_SHOWDOWN = 'js/showdown.js'
CLASS_RICHTEXTAREA = 'rich_text_area'
CSS_RICHTEXTAREA = 'css/editor.css'

JS_GENERIC_LOOKUP = 'js/admin/GenericRelatedObjectLookups.js'
CLASS_TARGECT = 'target_ct'
CLASS_TARGEID = 'target_id'

JS_LISTING_CATEGORY = 'js/listing.js'
CLASS_LISTING_CATEGORY = 'listing_category'
JS_PLACEMENT_CATEGORY = 'js/placement_category.js'
CLASS_PLACEMENT_CATEGORY = 'placement_category'

# Generic suggester media files
JS_GENERIC_SUGGEST = 'js/generic.suggest.js'
CSS_GENERIC_SUGGEST = 'css/generic.suggest.css'

# Fake windows
JS_JQUERY_UI = 'js/jquery-ui.js'


class ContentTypeWidget(forms.Select):
    " Custom widget adding a class to attrs. "
    def __init__(self, attrs={}):
        super(ContentTypeWidget, self).__init__(attrs={'class': CLASS_TARGECT})

class ForeignKeyGenericRawIdWidget(forms.TextInput):
    " Custom widget adding a class to attrs. "
    class Media:
        js = (
            settings.ADMIN_MEDIA_PREFIX + JS_GENERIC_LOOKUP,
        )
    def __init__(self, attrs={}):
        super(ForeignKeyGenericRawIdWidget, self).__init__(attrs={'class': CLASS_TARGEID})

class ExtendedRelatedFieldWidgetWrapper(widgets.RelatedFieldWidgetWrapper):
    'Custom widget to be used in admin that includes name and link to the target.'
    def __call__(self, name, value, *args, **kwargs):
        rel_to = self.rel.to
        related_url = '../../../%s/%s/%s/' % (rel_to._meta.app_label, rel_to._meta.object_name.lower(), value)
        output = [self.render_func(name, value, *args, **kwargs)]
        if value and rel_to in self.admin_site._registry: # If the related object has an admin interface:
            output.append(u'<a href="%s">%s</a>' % (related_url, rel_to.objects.get(pk=value)))
        return mark_safe(u''.join(output))

if 'ella.newman' in settings.INSTALLED_APPS:
    from djangomarkup.widgets import RichTextAreaWidget
    class RichTextAreaWidget(RichTextAreaWidget):
        'Widget representing the RichTextEditor. '
        class Media:
            js = (
                settings.ADMIN_MEDIA_PREFIX + JS_EDITOR,
                settings.ADMIN_MEDIA_PREFIX + JS_SHOWDOWN,
                # FIXME: i don't know why js is not loaded in ListingCategoryWidget
                settings.ADMIN_MEDIA_PREFIX + JS_PLACEMENT_CATEGORY,
                settings.ADMIN_MEDIA_PREFIX + JS_LISTING_CATEGORY,
            )
            css = {
                'screen': (settings.ADMIN_MEDIA_PREFIX + CSS_RICHTEXTAREA,),
            }
        def __init__(self, height=None, attrs={}):
            css_class = CLASS_RICHTEXTAREA
            if height:
                css_class += ' %s' % height
            super(RichTextAreaWidget, self).__init__(attrs={'class': css_class})

class GenericSuggestAdminWidget(forms.TextInput):
    class Media:
        js = (settings.ADMIN_MEDIA_PREFIX + JS_JQUERY_UI, settings.ADMIN_MEDIA_PREFIX + JS_GENERIC_SUGGEST,)
        css = {'screen': (settings.ADMIN_MEDIA_PREFIX + CSS_GENERIC_SUGGEST,),}

    def __init__(self, data, attrs={}, **kwargs):
        self.db_field, self.ownmodel, self.lookups = data
        self.model = self.db_field.rel.to
        self.is_hidden = True

        super(self.__class__, self).__init__(attrs)

    def render(self, name, value, attrs=None):

        # related_url for standard lookup and clreate suggest_url for JS suggest
        related_url = '../../../%s/%s/' % (self.model._meta.app_label, self.model._meta.object_name.lower())
        suggest_params = '&amp;'.join([ 'f=%s' % l for l in self.lookups ]) + '&amp;q='
        suggest_url = related_url + 'suggest/?' + suggest_params

        if self.db_field.rel.limit_choices_to:
            url = '?' + '&amp;'.join(['%s=%s' % (k, v) for k, v in self.db_field.rel.limit_choices_to.items()])
        else:
            url = ''

        attrs['class'] = 'vForeignKeyRawIdAdminField hidden'
        suggest_css_class = 'GenericSuggestField'

        if not value:
            suggest_item = ''
        else:
            try:
                suggest_item = '<li class="suggest-selected-item">%s <a class="suggest-delete-link">x</a></li>' % getattr(self.model.objects.get(pk=value), self.lookups[0])
            except self.model.DoesNotExist:
                suggest_item = ''

        output = [super(GenericSuggestAdminWidget, self).render(name, value, attrs)]

        output.append('<ul class="%s">%s<li><input type="text" id="id_%s_suggest" rel="%s" /></li></ul> ' \
                      % (suggest_css_class, suggest_item, name, suggest_url))
        # TODO: "id_" is hard-coded here. This should instead use the correct
        # API to determine the ID dynamically.
        output.append('<a href="%s%s" class="suggest-related-lookup" id="lookup_id_%s" onclick="return showRelatedObjectLookupPopup(this);"> ' % \
            (related_url, url, name))
        output.append('<img src="%simg/admin/selector-search.gif" width="16" height="16" alt="Lookup" /></a>' % settings.ADMIN_MEDIA_PREFIX)
        return mark_safe(u''.join(output))

class GenericSuggestAdminWidgetMultiple(forms.TextInput):
    class Media:
        js = (settings.ADMIN_MEDIA_PREFIX + JS_JQUERY_UI, settings.ADMIN_MEDIA_PREFIX + JS_GENERIC_SUGGEST,)
        css = {'screen': (settings.ADMIN_MEDIA_PREFIX + CSS_GENERIC_SUGGEST,),}

    def __init__(self, data, attrs={}, **kwargs):
        self.db_field, self.ownmodel, self.lookups = data
        self.model = self.db_field.rel.to
        self.is_hidden = True

        super(self.__class__, self).__init__(attrs)

    def render(self, name, value, attrs=None):

        # related_url for standard lookup and clreate suggest_url for JS suggest
        related_url = '../../../%s/%s/' % (self.model._meta.app_label, self.model._meta.object_name.lower())
        suggest_params = '&amp;'.join([ 'f=%s' % l for l in self.lookups ]) + '&amp;q='
        suggest_url = related_url + 'suggest/?' + suggest_params

        if self.db_field.rel.limit_choices_to:
            url = '?' + '&amp;'.join(['%s=%s' % (k, v) for k, v in self.db_field.rel.limit_choices_to.items()])
        else:
            url = ''

        attrs['class'] = 'vManyToManyRawIdAdminField hidden'
        suggest_css_class = 'GenericSuggestFieldMultiple'

        if not value:
            suggest_items = ''
        else:
            if not isinstance(value, (list, tuple)):
                value = [int(v) for v in value.split(',')]
            try:
                suggest_items = ''.join('<li class="suggest-selected-item">%s <a class="suggest-delete-link">x</a></li>' % \
                                         getattr(i, self.lookups[0]) for i in self.model.objects.filter(pk__in=value))
                value = ','.join(["%s" % v for v in value])
            except self.model.DoesNotExist:
                suggest_items = ''

        output = [super(GenericSuggestAdminWidgetMultiple, self).render(name, value, attrs)]

        output.append('<ul class="%s">%s<li><input type="text" id="id_%s_suggest" rel="%s" /></li></ul> ' \
                      % (suggest_css_class, suggest_items, name, suggest_url))
        # TODO: "id_" is hard-coded here. This should instead use the correct
        # API to determine the ID dynamically.
        output.append('<a href="%s%s" class="suggest-related-lookup" id="lookup_id_%s" onclick="return showRelatedObjectLookupPopup(this);"> ' % \
            (related_url, url, name))
        output.append('<img src="%simg/admin/selector-search.gif" width="16" height="16" alt="Lookup" /></a>' % settings.ADMIN_MEDIA_PREFIX)
        return mark_safe(u''.join(output))


class ListingCategoryWidget(forms.Select):
    """register javascript for duplicating main category to edit inline listing"""
    class Media:
        js = (
            settings.ADMIN_MEDIA_PREFIX + JS_LISTING_CATEGORY,
        )

    def __init__(self, attrs={}):
        super(ListingCategoryWidget, self).__init__(attrs={'class': CLASS_LISTING_CATEGORY})

class IncrementWidget(forms.TextInput):
    'Self incrementing widget.'
    class Media:
        js = (
            settings.ADMIN_MEDIA_PREFIX + 'js/increment.js',
    )
    def __init__(self, attrs={}):
        super(IncrementWidget, self).__init__(attrs={'class': 'increment'})

class ParagraphInputWidget(forms.HiddenInput):
    """show value without simpe way editing it"""
    def render(self, name, value, attrs=None):
        return mark_safe(u'<p>%s</p>%s' % (value, super(ParagraphInputWidget, self).render(name, value, attrs)))

class ForeignKeyRawIdWidget(widgets.ForeignKeyRawIdWidget):
    def label_for_value(self, value):
        obj = self.rel.to.objects.get(pk=value)
        label = truncate_words(obj, 14)
        adm = admin_url(obj)
        return '&nbsp;<a href="%s">%s</a>' % (adm, label)


""" """
class ListingCustomWidget(forms.SelectMultiple):
    def __init__(self, attrs=None, choices=(), *args, **kwargs):
        #attrs['class'] = 'listings'
        # TODO bug? Ask Honza, if selected choices should be provided in args, kwargs, somewhere..
        if not attrs or 'class' not in attrs:
            my_attrs = {'class': 'listings'}
        else:
            my_attrs = attrs
        super(ListingCustomWidget, self).__init__(attrs=my_attrs, choices=choices)

    def render(self, name, value, attrs=None, choices=()):
        cx = Context()
        cx['ADMIN_MEDIA_PREFIX'] = settings.ADMIN_MEDIA_PREFIX
        cx['id_prefix'] = name
        cx['verbose_name_publish_from'] = Listing._meta.get_field('publish_from').verbose_name.__unicode__()
        cx['choices'] = choices or self.choices
        cx['listings'] = list(value[0]) or []
        
        tpl = get_template('admin/widget/listing_custom.html')
        return mark_safe(tpl.render(cx))
""" """
