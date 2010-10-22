from datetime import datetime
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from ella.core.cache.utils import CachedGenericForeignKey, get_cached_object,\
    register_cache_invalidator

class DefaultCommentOptions(object):

    blocked = False
    premoderated = False
    check_profanities = True


class CommentOptionsManager(models.Manager):

    def contribute_to_class(self, model, name):
        super(CommentOptionsManager, self).contribute_to_class(model, name)
        register_cache_invalidator(model, 'target_ct', 'target_id')

    def get_for_object(self, object):
        ct, id = ContentType.objects.get_for_model(object), object.pk
        try:
            #return get_cached_object(CommentOptionsObject, target_ct=ct, target_id=id)
            return self.get(target_ct=ct, target_id=id)
        except CommentOptionsObject.DoesNotExist:
            return DefaultCommentOptions()


class CommentOptionsObject(models.Model):
    """contains comment options string for object"""

    objects = CommentOptionsManager()

    target_ct = models.ForeignKey(ContentType, verbose_name=_('Target content type'))
    target_id = models.PositiveIntegerField(_('Target id'))
    target = CachedGenericForeignKey(ct_field="target_ct", fk_field="target_id")

    blocked = models.BooleanField(_('Disable comments'), default=False)
    premoderated = models.BooleanField(_('Show comments only after approval'), default=False)
    check_profanities = models.BooleanField(_('Check profanities in comments'), default=False, editable=False)

    def __unicode__(self):
        return u"%s: %s" % (_("Comment Options"), self.target)

    class Meta:
        unique_together = (('target_ct', 'target_id',),)
        verbose_name = _('Comment Options')
        verbose_name_plural = _('Comment Options')

class BannedIP(models.Model):
    """
    """
    created = models.DateTimeField(_('Created'), default=datetime.now, editable=False)
    ip_address = models.IPAddressField(_('IP Address'), unique=True)
    reason = models.CharField(_('Reason'), max_length=255, blank=True, null=True)

    def __unicode__(self):
        return self.ip_address

    class Meta:
        verbose_name = _('Banned IP')
        verbose_name_plural = _('Banned IPs')
        ordering = ('-created',)
