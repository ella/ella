from datetime import datetime

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from ella.photos.models import Photo
from ella.core.box import Box
from ella.core.cache import get_cached_object


UPLOAD_TO = getattr(settings, 'ATTACHMENTS_UPLOAD_TO', 'attach/%Y/%m/%d')


class AttachmentBox(Box):
    def _get_template_list(self):
        """
        slightly patched version of Box._get_template_list
        TODO: ugly ;)
        """
        t_list = []
        if hasattr(self.obj, 'category_id') and self.obj.category_id:
            from ella.core.models import Category
            cat = get_cached_object(Category, pk=self.obj.category_id)
            base_path = 'box/category/%s/content_type/%s.%s/' % (cat.path, self.obj._meta.app_label, self.obj._meta.module_name)
            if hasattr(self.obj, 'slug'):
                t_list.append(base_path + 'attachment_type/%s/%s/%s.html' % (self.obj.type.name, self.obj.slug, self.box_type,))
                t_list.append(base_path + '%s/%s.html' % (self.obj.slug, self.box_type,))
            t_list.append(base_path + 'attachment_type/%s/%s.html' % (self.obj.type.name, self.box_type,))
            t_list.append(base_path + 'attachment_type/%s/box.html' % self.obj.type.name)
            t_list.append(base_path + '%s.html' % (self.box_type,))
            t_list.append(base_path + 'box.html')

        base_path = 'box/content_type/%s.%s/' % (self.obj._meta.app_label, self.obj._meta.module_name)
        if hasattr(self.obj, 'slug'):
            t_list.append(base_path + 'attachment_type/%s/%s/%s.html' % (self.obj.type.name, self.obj.slug, self.box_type,))
            t_list.append(base_path + '%s/%s.html' % (self.obj.slug, self.box_type,))
        t_list.append(base_path + 'attachment_type/%s/%s.html' % (self.obj.type.name, self.box_type,))
        t_list.append(base_path + 'attachment_type/%s/box.html' % self.obj.type.name)
        t_list.append(base_path + '%s.html' % (self.box_type,))
        t_list.append(base_path + 'box.html')

        t_list.append('box/attachment_type/%s/%s.html' % (self.obj.type.name, self.box_type))
        t_list.append('box/attachment_type/%s/box.html' % self.obj.type.name)
        t_list.append('box/%s.html' % self.box_type)
        t_list.append('box/box.html')

        return t_list

class Type(models.Model):
    name = models.CharField(_('Name'), max_length=100)
    mimetype = models.CharField(_('Mime type'), max_length=100,
            help_text=_('consult http://www.sfsu.edu/training/mimetype.htm'))

    class Meta:
        ordering=('name',)
        unique_together = (('name', 'mimetype'),)
        verbose_name = _('Type')
        verbose_name_plural = _('Types')

    def __unicode__(self):
        return self.name

class Attachment(models.Model):
    box_class = AttachmentBox

    name = models.CharField(_('Name'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=255)

    photo = models.ForeignKey(Photo, blank=True, null=True, verbose_name=_('Photo'))
    description = models.TextField(_('Description'))

    created = models.DateTimeField(_('Created'), default=datetime.now, editable=False)

    attachment = models.FileField(_('Attachment'), upload_to=UPLOAD_TO)

    type = models.ForeignKey(Type, verbose_name=_('Attachment type'))

    class Meta:
        ordering=('created',)
        verbose_name = _('Attachment')
        verbose_name_plural = _('Attachments')

    def __unicode__(self):
        return self.name

