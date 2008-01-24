from django import newforms as forms
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.contrib.admin import widgets

JS_EDITOR = 'js/editor.js'
JS_SHOWDOWN = 'js/showdown.js'
CLASS_RICHTEXTAREA = 'rich_text_area'
CSS_RICHTEXTAREA = 'css/editor.css'

JS_GENERIC_LOOKUP = 'js/admin/GenericRelatedObjectLookups.js'
CLASS_TARGECT = 'target_ct'
CLASS_TARGEID = 'target_id'

JS_LISTING_CATEGORY = 'js/listing.js'
CLASS_LISTING_CATEGORY = 'listing_category'


class ContentTypeWidget(forms.Select):
    def __init__(self, attrs={}):
        super(ContentTypeWidget, self).__init__(attrs={'class': CLASS_TARGECT})

class ForeignKeyRawIdWidget(forms.TextInput):
    class Media:
        js = (
            settings.ADMIN_MEDIA_PREFIX + JS_GENERIC_LOOKUP,
)
    def __init__(self, attrs={}):
        super(ForeignKeyRawIdWidget, self).__init__(attrs={'class': CLASS_TARGEID})

#class ExtendedforeignKeyRawIdWidget(forms.Select):
#    def render(self, name, value, attrs=None):
#        s = super(ExtendedforeignKeyRawIdWidget, self).render(name, value, attrs)
#        return u'%s asdfasdf' % s

class ExtendedRelatedFieldWidgetWrapper(widgets.RelatedFieldWidgetWrapper):
    def __call__(self, name, value, *args, **kwargs):
        from django.utils.safestring import mark_safe
        rel_to = self.rel.to
        related_url = '../../../%s/%s/%s' % (rel_to._meta.app_label, rel_to._meta.object_name.lower(), value)
        output = [self.render_func(name, value, *args, **kwargs)]
        if value and rel_to in self.admin_site._registry: # If the related object has an admin interface:
            output.append(u'<a href="%s">%s</a>' % (related_url, rel_to.objects.get(pk=value)))
        return mark_safe(u''.join(output))

class RichTextAreaWidget(forms.Textarea):
    class Media:
        js = (
            settings.ADMIN_MEDIA_PREFIX + JS_EDITOR,
            settings.ADMIN_MEDIA_PREFIX + JS_SHOWDOWN,
)
        css = {
            'screen': (settings.ADMIN_MEDIA_PREFIX + CSS_RICHTEXTAREA,),
}
    def __init__(self, attrs={}):
        super(RichTextAreaWidget, self).__init__(attrs={'class': CLASS_RICHTEXTAREA})

class ListingCategoryWidget(forms.Select):
    class Media:
        js = (
            settings.ADMIN_MEDIA_PREFIX + JS_LISTING_CATEGORY,
)
    def __init__(self, attrs={}):
        super(ListingCategoryWidget, self).__init__(attrs={'class': CLASS_LISTING_CATEGORY})

class IncrementWidget(forms.TextInput):
    class Media:
        js = (
            settings.ADMIN_MEDIA_PREFIX + 'js/increment.js',
)
    def __init__(self, attrs={}):
        super(IncrementWidget, self).__init__(attrs={'class': 'increment'})

class ParagraphInputWidget(forms.HiddenInput):
    def render(self, name, value, attrs=None):
        return mark_safe(u'<p>%s</p>%s' % (value, super(self.__class__, self).render(name, value, attrs)))

