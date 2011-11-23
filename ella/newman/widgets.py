from itertools import chain

from django import forms
from django.utils.safestring import mark_safe
from django.db.models.fields.related import ForeignKey
from django.contrib.admin import widgets
from django.template import Context
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.text import truncate_words
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from ella.core.conf import core_settings
from ella.core.models import Listing
from ella.photos.models import Photo
from djangomarkup.widgets import RichTextAreaWidget
from ella.newman.conf import newman_settings
from ella.newman.widget_extensions import rich_text_extensions

__all__ = [
    'NewmanRichTextAreaWidget', 'FlashImageWidget',
    'AdminSuggestWidget', 'DateWidget', 'DateTimeWidget',
    'ForeignKeyRawIdWidget', 'ForeignKeyGenericRawIdWidget',
    'ContentTypeWidget', 'OrderFieldWidget',
    'IncrementWidget', 'ListingCustomWidget',
    'GalleryItemContentTypeWidget',
]

# Rich text editor
#JS_MARKITUP = 'js/markitup/jquery.markitup.js'
JS_MARKITUP = 'js/fuckitup.js'
#JS_MARKITUP_SET = 'js/markitup/sets/%s/set.js' % MARKITUP_SET
JS_MARKITUP_SET = 'js/fuckitup_install.js'
CSS_MARKITUP = 'js/markitup/skins/markitup/style.css'
CSS_MARKITUP_SET = 'js/markitup/sets/%s/style.css' % newman_settings.MARKITUP_SET
CLASS_RICHTEXTAREA = 'rich_text_area'
JS_AUTOGROW = 'jquery/jquery.autogrow.js'

# Generic suggester media files
JS_GENERIC_SUGGEST = 'js/generic.suggest.js'
CSS_GENERIC_SUGGEST = 'css/generic.suggest.css'

# Other JS libs
CSS_JQUERY_UI = 'jquery/jquery-ui-smoothness.css'
JS_JQUERY_UI = 'jquery/jquery-ui.js'
JS_JQUERY_MOUSEWHEEL = 'jquery/jquery-mousewheel.js'
JS_JQUERY_FIELDSELECTION = 'jquery/jquery-fieldselection.js'

# Date and DateTime
JS_DATE_INPUT = 'js/datetime.js'
CSS_DATE_INPUT = 'css/datetime.css'

# Flash image uploader / editor
JS_FLASH_IMAGE_INPUT = 'js/flash_image.js'
SWF_FLASH_IMAGE_INPUT = 'swf/PhotoUploader.swf'

# Related/Generic lookups
JS_RELATED_LOOKUP = 'js/related_lookup.js'
CLASS_TARGECT = 'target_ct'
CLASS_TARGEID = 'target_id'

class NewmanRichTextAreaWidget(RichTextAreaWidget):
    """
    Newman's implementation of markup, based on markitup editor.
    """

    def __init__(self, attrs={}):
        css_class = CLASS_RICHTEXTAREA
        super(RichTextAreaWidget, self).__init__(attrs={'class': css_class})
        
    def _media(self):
        return forms.Media(
            js=[
                newman_settings.MEDIA_PREFIX + JS_MARKITUP,
                newman_settings.MEDIA_PREFIX + JS_MARKITUP_SET,
                newman_settings.MEDIA_PREFIX + JS_JQUERY_UI,
                newman_settings.MEDIA_PREFIX + JS_JQUERY_FIELDSELECTION,
                newman_settings.MEDIA_PREFIX + JS_AUTOGROW,
            ] + rich_text_extensions.get_js_extensions(),
            css={
                'screen': [
                    newman_settings.MEDIA_PREFIX + CSS_MARKITUP,
                    newman_settings.MEDIA_PREFIX + CSS_MARKITUP_SET,
                    newman_settings.MEDIA_PREFIX + CSS_JQUERY_UI,
                ] + rich_text_extensions.get_css_extensions(),
            }
        )
    media = property(_media)

class FlashImageWidget(widgets.AdminFileWidget):
    class Media:
        js = (
            newman_settings.MEDIA_PREFIX + JS_FLASH_IMAGE_INPUT,
        )

    def render(self, name, value, attrs=None):
        max_size = {'w': 1024, 'h': 768}
        swf_path = '%s%s' % (newman_settings.MEDIA_PREFIX, SWF_FLASH_IMAGE_INPUT,)
        lang_url = "%sswf/lang/%s.xml" % (newman_settings.MEDIA_PREFIX, settings.LANGUAGE_CODE,)
        if value:
            photo_flash_var = "&photoURL=%s" % value.url
        else:
            photo_flash_var = ""

        embed_code = u"""
        <object classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000"
        id="PhotoUploader" width="100%%" height="60px"
        codebase="http://fpdownload.macromedia.com/get/flashplayer/current/swflash.cab">
        <param name="movie" value="%(swf_path)s" />
        <param name="quality" value="high" />
        <param name="bgcolor" value="#869ca7" />
        <param name="allowScriptAccess" value="always" />
        <param name="FlashVars" value="max_width=%(max_width)s&max_height=%(max_height)s&value=%(value)s&languageURL=%(lang_url)s%(photo_flash_var)s" />
        <param name="allowFullScreen" value="true" />
        <param name="wmode" value="opaque" />
            <embed src="%(swf_path)s" quality="high" bgcolor="#869ca7"
            width="100%%" height="60px" name="PhotoUploader" align="middle"
            play="true"
            loop="false"
            quality="high"
            allowScriptAccess="always"
            type="application/x-shockwave-flash"
            pluginspage="http://www.adobe.com/go/getflashplayer"
            FlashVars="max_width=%(max_width)s&max_height=%(max_height)s&value=%(value)s&languageURL=%(lang_url)s%(photo_flash_var)s"
            allowFullScreen="true"
            wmode="opaque">
            </embed>
        </object>
        """ % {
            'swf_path': swf_path,
            'value': value,
            'lang_url': lang_url,
            'photo_flash_var': photo_flash_var,
            'max_width': max_size['w'],
            'max_height': max_size['h'],
        }

        return mark_safe(embed_code)


class AdminSuggestWidget(forms.TextInput):
    class Media:
        js = (newman_settings.MEDIA_PREFIX + JS_RELATED_LOOKUP, newman_settings.MEDIA_PREFIX + JS_GENERIC_SUGGEST,)
        css = {'screen': (newman_settings.MEDIA_PREFIX + CSS_GENERIC_SUGGEST,),}

    def __init__(self, db_field, attrs={}, **kwargs):
        self.db_field = db_field
        self.ownmodel = kwargs.pop('model')
        self.lookups = kwargs.pop('lookup')
        self.model = self.db_field.rel.to
        self.is_hidden = True

        super(AdminSuggestWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):

        # related_url for standard lookup and clreate suggest_url for JS suggest
        related_url = '/%s/%s/' % (self.model._meta.app_label, self.model._meta.object_name.lower())
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
                    sv = getattr(self.model.objects.get(pk=value), self.lookups[0])
                    if callable(sv): sv = sv()
                    suggest_items = '<li class="suggest-selected-item">%s <a class="suggest-delete-link">x</a></li>' % sv
                else:
                    if not isinstance(value, (list, tuple)):
                        value = [int(v) for v in value.split(',')]
                    suggest_items = []
                    for i in self.model.objects.filter(pk__in=value):
                        sv = getattr(i, self.lookups[0])
                        if callable(sv): sv = sv()
                        suggest_items.append('<li class="suggest-selected-item">%s <a class="suggest-delete-link">x</a></li>' % sv)
                    suggest_items = "".join(suggest_items)
                    value = ','.join(["%s" % v for v in value])
            except self.model.DoesNotExist:
                suggest_items = ''


        output = [super(AdminSuggestWidget, self).render(name, value, attrs)]

        output.append('<ul class="%s">%s<li><input type="text" id="id_%s_suggest" rel="%s" /></li></ul> ' \
                      % (suggest_css_class, suggest_items, name, suggest_url))
        # TODO: "id_" is hard-coded here. This should instead use the correct
        # API to determine the ID dynamically.
        output.append('<a href="%s%s?pop" class="suggest-related-lookup" id="lookup_id_%s"> ' % \
            (related_url, url, name))
        output.append('<img src="%sico/16/search.png" width="16" height="16" /></a>' % newman_settings.MEDIA_PREFIX)
        #output.append('<div class="form-row-tooltip">%s</div>' % ugettext('Type the first few letters for suggestions, then use the UP and DOWN arrows to select and hit ENTER to add or replace item.'))
        return mark_safe(u''.join(output))

class DateWidget(forms.DateInput):
    class Media:
        js = (
            newman_settings.MEDIA_PREFIX + JS_DATE_INPUT,
            newman_settings.MEDIA_PREFIX + JS_JQUERY_UI,
            newman_settings.MEDIA_PREFIX + JS_JQUERY_MOUSEWHEEL,
        )
        css = {'screen': (
            newman_settings.MEDIA_PREFIX + CSS_DATE_INPUT,
            newman_settings.MEDIA_PREFIX + CSS_JQUERY_UI,
        )}

    def render(self, name, value, attrs=None):
        attrs['class'] = 'vDateInput'
        return super(DateWidget, self).render(name, value, attrs)

class DateTimeWidget(forms.DateTimeInput):

    class Media:
        js = (
            newman_settings.MEDIA_PREFIX + JS_DATE_INPUT,
            newman_settings.MEDIA_PREFIX + JS_JQUERY_UI,
            newman_settings.MEDIA_PREFIX + JS_JQUERY_MOUSEWHEEL,
        )
        css = {'screen': (
            newman_settings.MEDIA_PREFIX + CSS_DATE_INPUT,
            newman_settings.MEDIA_PREFIX + CSS_JQUERY_UI,
        )}

    def render(self, name, value, attrs={}):
        attrs['class'] = 'vDateTimeInput'
        if value and hasattr(value, 'second') and not value.second:
            self.format = '%Y-%m-%d %H:%M'
        return super(DateTimeWidget, self).render(name, value, attrs)

class ForeignKeyRawIdWidget(forms.TextInput):

    class Media:
        js = (newman_settings.MEDIA_PREFIX + JS_RELATED_LOOKUP,)

    def __init__(self, rel, attrs=None):
        self.rel = rel
        super(ForeignKeyRawIdWidget, self).__init__(attrs)

    def _get_obj(self, value):
        if hasattr(self, '_object'):
            return self._object
        self._object = self.rel.to.objects.get(pk=value)
        return self._object

    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}
        related_url = '../../../%s/%s/' % (self.rel.to._meta.app_label, self.rel.to._meta.object_name.lower())
        url = ''
        if not attrs.has_key('class'):
            attrs['class'] = 'vForeignKeyRawIdAdminField' # The JavaScript looks for this hook.

        output = []
        if value and issubclass(self.rel.to, Photo):
            obj = self._get_obj(value)
            output.append('<span class="widget-thumb">%s</span>' % obj.thumb())
        output.append(super(ForeignKeyRawIdWidget, self).render(name, value, attrs))
        output.append(' <a href="%s%s?pop" class="rawid-related-lookup" id="lookup_id_%s">' % \
            (related_url, url, name))
        output.append('<img src="%sico/16/search.png" width="16" height="16" /></a>' % newman_settings.MEDIA_PREFIX)
        if value:
            output.append(self.label_for_value(value))
        return mark_safe(u''.join(output))

    def label_for_value(self, value):
        obj = self._get_obj(value)
        obj_url = '/%s/%s/%s/' % (self.rel.to._meta.app_label, self.rel.to._meta.object_name.lower(), obj.pk)
        label = truncate_words(obj, 14)
        return '&nbsp;<a class="js-hashadr" href="%s">%s</a>' % (obj_url, label)


class ForeignKeyGenericRawIdWidget(forms.TextInput):
    " Custom widget adding a class to attrs. "

    class Media:
        js = (newman_settings.MEDIA_PREFIX + JS_RELATED_LOOKUP,)

    def __init__(self, attrs={}):
        super(ForeignKeyGenericRawIdWidget, self).__init__(attrs={'class': CLASS_TARGEID})

    def render(self, name, value, attrs=None):
        output = [super(ForeignKeyGenericRawIdWidget, self).render(name, value, attrs)]
        output.append('<a class="generic-related-lookup" id="lookup_id_%s"> ' % name)
        output.append('<img src="%sico/16/search.png" width="16" height="16" /></a>' % newman_settings.MEDIA_PREFIX)
        return mark_safe(''.join(output))


class ContentTypeWidget(forms.Select):
    " Custom widget adding a class to attrs. "
    def __init__(self, attrs={}):
        super(ContentTypeWidget, self).__init__(attrs={'class': CLASS_TARGECT})

    @property
    def applicable_ct_pks(self):
        from ella.newman import site
        return [ct.pk for ct in site.applicable_content_types]

    def render_options(self, choices, selected_choices):
        def render_option(option_value, option_label):
            option_value = force_unicode(option_value)
            selected_html = (option_value in selected_choices) and u' selected="selected"' or ''
            return u'<option value="%s"%s>%s</option>' % (
                escape(option_value), selected_html, _(option_label))
        # Normalize to strings.
        selected_choices = set([force_unicode(v) for v in selected_choices])
        output = []
        applicable_ct_pks = self.applicable_ct_pks
        for option_value, option_label in chain(self.choices, choices):
            if option_value in applicable_ct_pks or not option_value:
                output.append(render_option(option_value, option_label))
        return u'\n'.join(output)


class OrderFieldWidget(forms.HiddenInput):
    def __init__(self, attrs={}):
        super(OrderFieldWidget, self).__init__(attrs={'class': 'item-order'})

class IncrementWidget(forms.TextInput):
    'Self incrementing widget.'
    class Media:
        js = (
            newman_settings.MEDIA_PREFIX + 'js/increment.js',
        )
    def __init__(self, attrs={}):
        super(IncrementWidget, self).__init__(attrs={'class': 'increment'})


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
        cx['NEWMAN_MEDIA_PREFIX'] = newman_settings.MEDIA_PREFIX
        cx['id_prefix'] = name
        cx['verbose_name_publish_from'] = Listing._meta.get_field('publish_from').verbose_name.__unicode__()
        cx['choices'] = choices or self.choices
        cx['render_commercial_switch'] = core_settings.LISTING_USE_COMMERCIAL_FLAG
        if len(value) == 1:
            cx['listings'] = value[0] or []
        tpl = get_template('newman/widget/listing_custom.html')
        return mark_safe(tpl.render(cx))

class ChoiceCustomWidget(forms.TextInput):
    def __init__(self, attrs=None, *args, **kwargs):
        if not attrs or 'class' not in attrs:
            my_attrs = {'class': 'choices'}
        else:
            my_attrs = attrs
        super(ChoiceCustomWidget, self).__init__(attrs=my_attrs)

    def render(self, name, value, attrs=None):
        cx = Context()
        cx['NEWMAN_MEDIA_PREFIX'] = newman_settings.MEDIA_PREFIX
        cx['id_prefix'] = name
        cx['choices'] = value
        tpl = get_template('newman/widget/poll_choices_custom.html')
        return mark_safe(tpl.render(cx))

    def _has_changed(self, initial, data):
        from ella.newman import fields
        initial_value = fields.ChoiceCustomField.default_text
        return super(ChoiceCustomWidget, self)._has_changed(initial_value, data)

class GalleryItemContentTypeWidget(forms.HiddenInput):
    " Custom hidden widget for gallery items. "

    def __init__(self, attrs={}):
        ct = ContentType.objects.get_for_model(Photo)
        super(GalleryItemContentTypeWidget, self).__init__(attrs={'class': CLASS_TARGECT, 'value': ct.pk})

