from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from ella.core.cache.utils import CachedGenericForeignKey, get_cached_object

class DefaultCommentOptions(object):

    blocked = False
    premoderated = False
    check_profanities = True


class CommentOptionsManager(models.Manager):

    def get_for_object(self, object):
        ct, id = ContentType.objects.get_for_model(object), object.pk
        try:
            return get_cached_object(CommentOptionsObject, target_ct=ct, target_id=id)
        except CommentOptionsObject.DoesNotExist:
            return DefaultCommentOptions()


class CommentOptionsObject(models.Model):
    """contains comment options string for object"""

    objects = CommentOptionsManager()

    target_ct = models.ForeignKey(ContentType, verbose_name=_('Target content type'))
    target_id = models.PositiveIntegerField(_('Target id'))
    target = CachedGenericForeignKey(ct_field="target_ct", fk_field="target_id")

    blocked = models.BooleanField(default=False)
    premoderated = models.BooleanField(default=False)
    check_profanities = models.BooleanField(default=False)

    def __unicode__(self):
        return u"%s: %s" % (_("Comment Options"), self.target)

    class Meta:
        unique_together = (('target_ct', 'target_id',),)
        verbose_name = _('Comment Options')
        verbose_name_plural = _('Comment Options')
