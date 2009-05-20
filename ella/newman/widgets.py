from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.db.models.fields.related import ForeignKey
from django.contrib.admin import widgets
from django.utils.text import truncate_words
from ella.ellaadmin.utils import admin_url
from djangomarkup.widgets import RichTextAreaWidget

MARKITUP_SET = getattr(settings, 'MARKDOWN', 'markdown')
MEDIA_PREFIX = getattr(settings, 'NEWMAN_MEDIA_PREFIX', settings.ADMIN_MEDIA_PREFIX)

# Rich text editor
JS_MARKITUP = 'js/markitup/jquery.markitup.js'
JS_MARKITUP_SET = 'js/markitup/sets/%s/set.js' % MARKITUP_SET
CSS_MARKITUP = 'js/markitup/skins/markitup/style.css'
CSS_MARKITUP_SET = 'js/markitup/sets/%s/style.css' % MARKITUP_SET
CLASS_RICHTEXTAREA = 'rich_text_area'

# Generic suggester media files
JS_GENERIC_SUGGEST = 'js/generic.suggest.js'
CSS_GENERIC_SUGGEST = 'css/generic.suggest.css'

# Other JS libs
CSS_JQUERY_UI = 'jquery/jquery-ui-smoothness.css'
JS_JQUERY_UI = 'jquery/jquery-ui.js'
JS_JQUERY_MOUSEWHEEL = 'jquery/jquery-mousewheel.js'

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
    class Media:
        js = (
            MEDIA_PREFIX + JS_MARKITUP,
            MEDIA_PREFIX + JS_MARKITUP_SET,
        )
        css = {
            'screen': (
                MEDIA_PREFIX + CSS_MARKITUP,
                MEDIA_PREFIX + CSS_MARKITUP_SET,
            ),
        }

    def __init__(self, attrs={}):
        css_class = CLASS_RICHTEXTAREA
        super(RichTextAreaWidget, self).__init__(attrs={'class': css_class})


class FlashImageWidget(widgets.AdminFileWidget):
    class Media:
        js = (
            settings.NEWMAN_MEDIA_PREFIX + JS_FLASH_IMAGE_INPUT,
        )

    def render(self, name, value, attrs=None):
        swf_path = '%s%s' % (settings.NEWMAN_MEDIA_PREFIX, SWF_FLASH_IMAGE_INPUT,)
        embed_code = u"""
        <object classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000"
        id="PhotoUploader" width="100%%" height="60px"
        codebase="http://fpdownload.macromedia.com/get/flashplayer/current/swflash.cab">
        <param name="movie" value="%s" />
        <param name="quality" value="high" />
        <param name="bgcolor" value="#869ca7" />
        <param name="allowScriptAccess" value="sameDomain" />
        <param name="FlashVars" value="max_width=&max_height=&value=%s" />
        <param name="allowFullScreen" value="true" />
        <param name="wmode" value="opaque" />
            <embed src="%s" quality="high" bgcolor="#869ca7"
            width="100%%" height="60px" name="PhotoUploader" align="middle"
            play="true"
            loop="false"
            quality="high"
            allowScriptAccess="sameDomain"
            type="application/x-shockwave-flash"
            pluginspage="http://www.adobe.com/go/getflashplayer"
            FlashVars="max_width=&max_height=&value=%s"
            allowFullScreen="true"
            wmode="opaque">
            </embed>
        </object>
        """ % (swf_path, value, swf_path, value)

        return mark_safe(embed_code)


class ForeignKeyRawIdWidget(forms.TextInput):

    class Media:
        js = (settings.NEWMAN_MEDIA_PREFIX + JS_RELATED_LOOKUP,)

    def __init__(self, rel, attrs=None):
        self.rel = rel
        super(ForeignKeyRawIdWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}
        related_url = '../../../%s/%s/' % (self.rel.to._meta.app_label, self.rel.to._meta.object_name.lower())
        url = ''
        if not attrs.has_key('class'):
            attrs['class'] = 'vForeignKeyRawIdAdminField' # The JavaScript looks for this hook.
        output = [super(ForeignKeyRawIdWidget, self).render(name, value, attrs)]
        output.append('<a href="%s%s?pop" class="rawid-related-lookup" id="lookup_id_%s"> ' % \
            (related_url, url, name))
        output.append('<img src="%sico/16/search.png" width="16" height="16" /></a>' % settings.NEWMAN_MEDIA_PREFIX)
        if value:
            output.append(self.label_for_value(value))
        return mark_safe(u''.join(output))

    def label_for_value(self, value):
        obj = self.rel.to.objects.get(pk=value)
        label = truncate_words(obj, 14)
        adm = admin_url(obj)
        return '&nbsp;<a href="%s">%s</a>' % (adm, label)


class AdminSuggestWidget(forms.TextInput):
    class Media:
        js = (settings.NEWMAN_MEDIA_PREFIX + JS_RELATED_LOOKUP, settings.NEWMAN_MEDIA_PREFIX + JS_GENERIC_SUGGEST,)
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
        output.append('<a href="%s%s?pop" class="suggest-related-lookup" id="lookup_id_%s"> ' % \
            (related_url, url, name))
        output.append('<img src="%sico/16/search.png" width="16" height="16" /></a>' % settings.NEWMAN_MEDIA_PREFIX)
        return mark_safe(u''.join(output))

class DateWidget(forms.DateInput):
    class Media:
        js = (
            settings.NEWMAN_MEDIA_PREFIX + JS_DATE_INPUT,
            settings.NEWMAN_MEDIA_PREFIX + JS_JQUERY_UI,
            settings.NEWMAN_MEDIA_PREFIX + JS_JQUERY_MOUSEWHEEL,
        )
        css = {'screen': (
            settings.NEWMAN_MEDIA_PREFIX + CSS_DATE_INPUT,
            settings.NEWMAN_MEDIA_PREFIX + CSS_JQUERY_UI,
        )}

    def render(self, name, value, attrs=None):
        attrs['class'] = 'vDateInput'
        return super(DateWidget, self).render(name, value, attrs)

class DateTimeWidget(forms.DateTimeInput):
    class Media:
        js = (
            settings.NEWMAN_MEDIA_PREFIX + JS_DATE_INPUT,
            settings.NEWMAN_MEDIA_PREFIX + JS_JQUERY_UI,
            settings.NEWMAN_MEDIA_PREFIX + JS_JQUERY_MOUSEWHEEL,
        )
        css = {'screen': (
            settings.NEWMAN_MEDIA_PREFIX + CSS_DATE_INPUT,
            settings.NEWMAN_MEDIA_PREFIX + CSS_JQUERY_UI,
        )}

    def render(self, name, value, attrs=None):
        attrs['class'] = 'vDateTimeInput'
        if value and not value.second:
            self.format = '%Y-%m-%d %H:%M'
        return super(DateTimeWidget, self).render(name, value, attrs)

# widgets from ellaadmin

class ForeignKeyGenericRawIdWidget(forms.TextInput):
    " Custom widget adding a class to attrs. "

    class Media:
        js = (settings.NEWMAN_MEDIA_PREFIX + JS_RELATED_LOOKUP,)

    def __init__(self, attrs={}):
        super(ForeignKeyGenericRawIdWidget, self).__init__(attrs={'class': CLASS_TARGEID})

    def render(self, name, value, attrs=None):
        output = [super(ForeignKeyGenericRawIdWidget, self).render(name, value, attrs)]
        output.append('<a class="generic-related-lookup" id="lookup_id_%s"> ' % name)
        output.append('<img src="%sico/16/search.png" width="16" height="16" /></a>' % settings.NEWMAN_MEDIA_PREFIX)
        return mark_safe(''.join(output))


class ContentTypeWidget(forms.Select):
    " Custom widget adding a class to attrs. "
    def __init__(self, attrs={}):
        super(ContentTypeWidget, self).__init__(attrs={'class': CLASS_TARGECT})

class IncrementWidget(forms.TextInput):
    'Self incrementing widget.'
    class Media:
        js = (
            MEDIA_PREFIX + 'js/increment.js',
        )
    def __init__(self, attrs={}):
        super(IncrementWidget, self).__init__(attrs={'class': 'increment'})


