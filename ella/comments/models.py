from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_str

from ella.comments import defaults, management
from ella.core.cache.utils import cache_this, method_key_getter, get_cached_object



class CommentOptions(models.Model):
    """
    contains options string for discussion
    with immediate effect

    TODO: options should not be string but boolean columns
    """
    target_ct = models.ForeignKey(ContentType, verbose_name=_('target content type'))
    target_id = models.PositiveIntegerField(_('target id'))
    options = models.CharField(maxlength=defaults.OPTS_LENGTH, blank=True)
    timestamp = models.DateTimeField(default=datetime.now)

    class Meta:
        verbose_name = _('Comment Options')
        verbose_name_plural = _('Comment Options')


def get_test_builder(object_order):
    def test_for_comment(*args, **kwargs):
        obj = args[object_order]
        return [ (Comment, lambda x: x.target == obj) ]
    return test_for_comment

class CommentManager(models.Manager):
    @cache_this(method_key_getter, get_test_builder(1))
    def get_count_for_object(self, object):
        target_ct = ContentType.objects.get_for_model(object)
        return self.filter(target_ct=target_ct, target_id=object.id).count()

class Comment(models.Model):
    # what is this comment for
    target_ct = models.ForeignKey(ContentType, verbose_name=_('target content type'))
    target_id = models.PositiveIntegerField(_('target id'))

    # comment content
    subject = models.TextField(_('comment subject'), maxlength=defaults.SUBJECT_LENGTH)
    content = models.TextField(_('comment content'), maxlength=defaults.COMMENT_LENGTH)
    # comment picture
#    image = models.ImageField(_('image answer'), upload_to='comment_image', blank=True, null=True)

    # tree structure
    parent = models.ForeignKey('self', verbose_name=_('tree structure parent'), blank=True, null=True)
    path = models.CharField(_('genealogy tree path'), maxlength=defaults.PATH_LENGTH, blank=True, editable=True)

    # author if is authorized
    user = models.ForeignKey(User, verbose_name=_('authorized author'), blank=True, null=True)
    # author otherwise
    nickname = models.CharField(_("anonymous author's nickname"), maxlength=defaults.NICKNAME_LENGTH, blank=True)
    email = models.EmailField(_('authors email (optional)'), blank=True)
    # authors ip address
    ip_address = models.IPAddressField(_('ip address'), blank=True, null=True)

    # comment metadata
    submit_date = models.DateTimeField(_('date/time submitted'), default=datetime.now, editable=True)
    is_public = models.BooleanField(_('is public'), default=True)

    objects = CommentManager()

    @property
    def is_authorized(self):
        if self.user:
            return True
        return False

    @property
    def is_thread_root(self):
        return self.path == ''

    @property
    def target(self):
        return get_cached_object(self.target_ct, pk=self.target_id)

    def get_genealogy_path(self):
        """genealogy tree structure field"""
        if self.parent and self.id:
            return '%s%s%x' % (self.parent.path, defaults.PATH_SEPARATOR, self.id)
        return ''

    def save(self):
        # TODO: maybe create models.GenealogyField for this
        # first save to obtain primary key
        super(Comment, self).save()
        # do not store too long path
        path = self.get_genealogy_path()
        if len(path) <= defaults.PATH_LENGTH:
            self.path = path
        else:
            self.path = parent.path
        # save it all
        super(Comment, self).save()

    def __unicode__(self):
        if self.id:
            return u"comment [id:%d] '%s...' on %s {path:%s}" % (self.id, self.content[:10],
                    self.target_ct.get_object_for_this_type(pk=self.target_id), self.path)
        return u"unsaved comment"

    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')



class BannedUser(models.Model):
    """
    model with generic relation on object - same as in comment model
    ban is global if there is no relation
    """
    target_ct = models.ForeignKey(ContentType, verbose_name=_('target content type'))
    target_id = models.PositiveIntegerField(_('target id'))
    user = models.ForeignKey(User, verbose_name=_('banned author'))

    class Meta:
        verbose_name = _('Banned User')
        verbose_name_plural = _('Banned Users')


class BannedIP(models.Model):
    """TODO"""
    pass



# Register the admin options for these models.
from django import VERSION
from django.contrib import admin

admin.site.register(Comment)
admin.site.register(BannedUser)
admin.site.register(CommentOptions)


