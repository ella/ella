from django import newforms as forms
from django.conf import settings
from django.contrib.admin import widgets
from django.utils.safestring import mark_safe


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
    " Custom widget adding a class to attrs. "
    def __init__(self, attrs={}):
        super(ContentTypeWidget, self).__init__(attrs={'class': CLASS_TARGECT})

class ForeignKeyRawIdWidget(forms.TextInput):
    " Custom widget adding a class to attrs. "
    class Media:
        js = (
            settings.ADMIN_MEDIA_PREFIX + JS_GENERIC_LOOKUP,
)
    def __init__(self, attrs={}):
        super(ForeignKeyRawIdWidget, self).__init__(attrs={'class': CLASS_TARGEID})

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
)
        css = {
            'screen': (settings.ADMIN_MEDIA_PREFIX + CSS_RICHTEXTAREA,),
}
    def __init__(self, height=None, attrs={}):
        css_class = CLASS_RICHTEXTAREA
        if height:
            css_class += ' %s' % height
        super(RichTextAreaWidget, self).__init__(attrs={'class': css_class})

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

