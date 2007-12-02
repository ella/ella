from django import newforms as forms
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

JS_EDITOR = 'js/editor.js'
JS_SHOWDOWN = 'js/showdown.js'
CLASS_RICHTEXTAREA = 'rich_text_area'
CSS_RICHTEXTAREA = 'css/pokus.css'

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

class RichTextAreaWidget(forms.Textarea):
    class Media:
        js = (
            settings.ADMIN_MEDIA_PREFIX + JS_EDITOR,
            settings.ADMIN_MEDIA_PREFIX + JS_SHOWDOWN,
)
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

class ParagraphWidget(forms.Widget):
    def render(self, name, value, attrs=None):
        return u'<p>%s</p>' % value

