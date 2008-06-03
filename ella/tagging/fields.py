"""
A custom Model Field for tagging.
"""
from django.db.models import signals
from django.db.models.fields import CharField
from django.dispatch import dispatcher
from django.utils.translation import ugettext_lazy as _

from ella.tagging import settings
from ella.tagging.models import Tag
from ella.tagging.utils import edit_string_for_tags
from ella.tagging.validators import isTagList

class TagField(CharField):
    """
    A "special" character field that actually works as a relationship to tags
    "under the hood". This exposes a space-separated string of tags, but does
    the splitting/reordering/etc. under the hood.
    """
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 255)
        kwargs['blank'] = kwargs.get('blank', True)
        kwargs['validator_list'] = [isTagList] + kwargs.get('validator_list', [])
        super(TagField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        super(TagField, self).contribute_to_class(cls, name)

        # Make this object the descriptor for field access.
        setattr(cls, self.name, self)

        # Save tags back to the database post-save
        dispatcher.connect(self._save, signal=signals.post_save, sender=cls)

    def __get__(self, instance, owner=None):
        """
        Tag getter. Returns an instance's tags if accessed on an instance, and
        all of a model's tags if called on a class. That is, this model::

           class Link(models.Model):
               ...
               tags = TagField()

        Lets you do both of these::

           >>> l = Link.objects.get(...)
           >>> l.tags
           'tag1 tag2 tag3'

           >>> Link.tags
           'tag1 tag2 tag3 tag4'

        """
        # Handle access on the model (i.e. Link.tags)
        if instance is None:
            return edit_string_for_tags(Tag.objects.usage_for_model(owner))

        tags = self._get_instance_tag_cache(instance)
        if tags is None:
            if instance.pk is None:
                self._set_instance_tag_cache(instance, '')
            else:
                self._set_instance_tag_cache(
                    instance, edit_string_for_tags(Tag.objects.get_for_object(instance)))
        return self._get_instance_tag_cache(instance)

    def __set__(self, instance, value):
        """
        Set an object's tags.
        """
        if instance is None:
            raise AttributeError(_('%s can only be set on instances.') % self.name)
        if settings.FORCE_LOWERCASE_TAGS and value is not None:
            value = value.lower()
        self._set_instance_tag_cache(instance, value)

    def _save(self, signal, sender, instance):
        """
        Save tags back to the database
        """
        tags = self._get_instance_tag_cache(instance)
        if tags is not None:
            Tag.objects.update_tags(instance, tags)

    def __delete__(self, instance):
        """
        Clear all of an object's tags.
        """
        self._set_instance_tag_cache(instance, '')

    def _get_instance_tag_cache(self, instance):
        """
        Helper: get an instance's tag cache.
        """
        return getattr(instance, '_%s_cache' % self.attname, None)

    def _set_instance_tag_cache(self, instance, tags):
        """
        Helper: set an instance's tag cache.
        """
        setattr(instance, '_%s_cache' % self.attname, tags)

    def get_internal_type(self):
        return 'CharField'

    def formfield(self, **kwargs):
        from ella.tagging import forms
        defaults = {'form_class': forms.TagField}
        defaults.update(kwargs)
        return super(TagField, self).formfield(**defaults)


# Helper
def tags2str(tagset):
    return u' '.join([t.name for t in tagset])


# --- suggest

from django import newforms as forms
from ella.ellaadmin import widgets as ellaadminwidgets
from ella.ellaadmin import options
from django.contrib.admin import widgets
from django.utils.safestring import mark_safe
from django.utils.encoding import smart_unicode
from django.conf import settings


JS_SUGGEST = 'js/jquery.suggest.js'
JS_SUGGEST_MULTIPLE = 'js/jquery.suggest.multiple.js'
CSS_SUGGEST = 'css/jquery.suggest.css'

class SuggestTagAdminWidget(forms.TextInput):

    class Media:
        js = (
            settings.ADMIN_MEDIA_PREFIX + JS_SUGGEST,
)
        css = {
            'screen': (settings.ADMIN_MEDIA_PREFIX + CSS_SUGGEST,),
}


    def __init__(self, db_field, attrs={}):
        self.rel = db_field.rel
        self.value = db_field
        super(SuggestTagAdminWidget, self).__init__(attrs)


    def render(self, name, value, attrs=None):
        if self.rel.limit_choices_to:
            url = '?' + '&amp;'.join(['%s=%s' % (k, v) for k, v in self.rel.limit_choices_to.items()])
        else:
            url = ''
        if not attrs.has_key('class'):
          attrs['class'] = 'vForeignKeyRawIdAdminField vSuggestField' # The JavaScript looks for this hook.
        if value:
            if type(value) in [long, int]:
                tag = Tag.objects.get(pk=value)
            elif type(value) in [str, unicode]:
                tag = Tag.objects.get(name=value)
            output = [super(SuggestTagAdminWidget, self).render(name, tag.name, attrs)]
        else:
            output = [super(SuggestTagAdminWidget, self).render(name, value, attrs)]
        return mark_safe(u''.join(output))



class SuggestTagAdminField(forms.fields.Field):
    default_error_messages = {
        'not_found': u'Tag "%s" is not found.',
        'found_too_much': u'Multiple tags found as "%s".',
}
    def __init__(self, db_field, *args, **kwargs):
        self.rel = db_field.rel
        self.widget = SuggestTagAdminWidget(db_field, **kwargs)
        super(SuggestTagAdminField, self).__init__(*args, **kwargs)


    def clean(self, value):
        from django.newforms.util import ValidationError
        super(SuggestTagAdminField, self).clean(value)
        isFound = Tag.objects.filter(name=value)
        if len(isFound) == 1:
            tag = isFound[0]
        elif len(isFound) > 1:
            raise ValidationError(self.error_messages['found_too_much'] % value)
        elif len(isFound) == 0:
            tag, status = Tag.objects.get_or_create(name=value)
            if not status:
                raise ValidationError(self.error_messages['not_found'] % value)
        return tag


class SuggestTagWidget(forms.TextInput):

    class Media:
        js = (
            settings.ADMIN_MEDIA_PREFIX + JS_SUGGEST_MULTIPLE,
)
        css = {
            'screen': (settings.ADMIN_MEDIA_PREFIX + CSS_SUGGEST,),
}


    def __init__(self, attrs={}):
        super(SuggestTagWidget, self).__init__(attrs)


    def render(self, name, value, attrs=None):
        if not attrs.has_key('class'):
          attrs['class'] = 'vSuggestMultipleField' # The JavaScript looks for this hook.
        output = [super(SuggestTagWidget, self).render(name, value, attrs)]
        return mark_safe(u''.join(output))


class SuggestTagField(forms.fields.Field):
    MULTIPLE_DIVIDER = ','
    default_error_messages = {
        'not_found': u'Tag "%s" is not found.',
        'found_too_much': u'Multiple tags found as "%s".',
}
    def __init__(self, *args, **kwargs):
        self.widget = SuggestTagWidget(**kwargs)
        super(SuggestTagField, self).__init__(*args, **kwargs)

    def clean(self, value):
        return smart_unicode(value)

