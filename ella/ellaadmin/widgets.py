from django import forms
from django.conf import settings
from django.contrib.admin import widgets
from django.utils.safestring import mark_safe
from django.utils.text import truncate_words

from ella.ellaadmin.utils import admin_url


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

JS_SUGGEST = 'js/jquery.suggest.js'
JS_SUGGEST_MULTIPLE = 'js/jquery.suggest.multiple.js'
CSS_SUGGEST = 'css/jquery.suggest.css'


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

class RichTextAreaWidget(forms.Textarea):
    'Widget representing the RichTextEditor. '
    class Media:
        js = (
            settings.ADMIN_MEDIA_PREFIX + JS_EDITOR,
            settings.ADMIN_MEDIA_PREFIX + JS_SHOWDOWN,
            settings.ADMIN_MEDIA_PREFIX + JS_PLACEMENT_CATEGORY,
)
        css = {
            'screen': (settings.ADMIN_MEDIA_PREFIX + CSS_RICHTEXTAREA,),
}
    def __init__(self, height=None, attrs={}):
        css_class = CLASS_RICHTEXTAREA
        if height:
            css_class += ' %s' % height
        super(RichTextAreaWidget, self).__init__(attrs={'class': css_class})

class CategorySuggestAdminWidget(forms.TextInput):
    class Media:
        js = (
            settings.ADMIN_MEDIA_PREFIX + JS_SUGGEST,
)
        css = {
            'screen': (settings.ADMIN_MEDIA_PREFIX + CSS_SUGGEST,),
}


    def __init__(self, db_field, attrs={}, **kwargs):
        self.rel = db_field.rel
        self.value = db_field
        super(self.__class__, self).__init__(attrs)


    def render(self, name, value, attrs=None):
        from ella.core.models import Category
        if self.rel.limit_choices_to:
            url = '?' + '&amp;'.join(['%s=%s' % (k, v) for k, v in self.rel.limit_choices_to.items()])
        else:
            url = ''
        if not attrs.has_key('class'):
          attrs['class'] = 'vForeignKeyRawIdAdminField vCatSuggestField' # The JavaScript looks for this hook.
        if value:
            try:
                if type(value) in [long, int]:
                    cat = Category.objects.get(pk=value)
                elif type(value) in [str, unicode]:
                    cat = Category.objects.get(tree_path=value)
                output = [super(self.__class__, self).render(name, "%s:%s" % (cat.site.name,cat.tree_path), attrs)]
            except Category.DoesNotExist:
                output = [super(self.__class__, self).render(name, value, attrs)]
        else:
            output = [super(self.__class__, self).render(name, '', attrs)]
        return mark_safe(u''.join(output))

class AuthorsSuggestAdminWidget(forms.TextInput):
    class Media:
        js = (
            settings.ADMIN_MEDIA_PREFIX + JS_SUGGEST_MULTIPLE,
)
        css = {
            'screen': (settings.ADMIN_MEDIA_PREFIX + CSS_SUGGEST,),
}


    def __init__(self, db_field, attrs={}, **kwargs):
        self.rel = db_field.rel
        self.value = db_field
        super(self.__class__, self).__init__(attrs)


    def render(self, name, value, attrs=None):
        from ella.core.models import Author
        if self.rel.limit_choices_to:
            url = '?' + '&amp;'.join(['%s=%s' % (k, v) for k, v in self.rel.limit_choices_to.items()])
        else:
            url = ''
        if not attrs.has_key('class'):
            attrs['class'] = 'vForeignKeyRawIdAdminField vSuggestMultipleFieldAuthor' # The JavaScript looks for this hook.
        if value:
            a_values = ''
            try:
                if type(value) == list:
                    a_lst = Author.objects.filter(pk__in=value)
                    for a in a_lst:
                        a_values += "%s:%s," % (a.pk, a.name)
                elif type(value) in [unicode, str]:
                    for a in value.split(','):
                        a_values += a + ','
                if a_values.endswith(','):
                    a_values = a_values[:-1]
                output = [super(self.__class__, self).render(name, a_values, attrs)]
            except:
                output = [super(self.__class__, self).render(name, value, attrs)]
        else:
            output = [super(self.__class__, self).render(name, '', attrs)]
        return mark_safe(u''.join(output))

class PlacementCategoryWidget(CategorySuggestAdminWidget):
    def __init__(self, db_field, attrs={}):
        self.rel = db_field.rel
        self.value = db_field
        super(self.__class__, self).__init__(attrs)

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

