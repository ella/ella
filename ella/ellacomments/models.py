from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from ella.core.cache.utils import CachedGenericForeignKey

class DefaultCommentOptions(object):

    blocked = False
    premoderated = False
    check_profanities = True


class CommentOptionsObject(models.Model):
    """contains comment options string for object"""
    target_ct = models.ForeignKey(ContentType, verbose_name=_('Target content type'))
    target_id = models.PositiveIntegerField(_('Target id'))
    target = CachedGenericForeignKey(ct_field="target_ct", fk_field="target_id")

    blocked = models.BooleanField()
    premoderated = models.BooleanField()
    check_profanities = models.BooleanField()

    def __unicode__(self):
        return u"%s: %s" % (_("Comment Options"), self.target)

    class Meta:
        unique_together = (('target_ct', 'target_id',),)
        verbose_name = _('Comment Options')
        verbose_name_plural = _('Comment Options')
