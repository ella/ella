from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_str

from ella.core.cache.utils import cache_this, method_key_getter, get_cached_object, get_cached_list

from ella.comments import defaults


class CommentOptions(models.Model):
    """
    contains options string for discussion
    with immediate effect

    TODO: options should not be string but boolean columns
    """
    target_ct = models.ForeignKey(ContentType, verbose_name=_('target content type'))
    target_id = models.PositiveIntegerField(_('target id'))
    target = generic.GenericForeignKey()
    options = models.CharField(max_length=defaults.OPTS_LENGTH, blank=True)
    timestamp = models.DateTimeField(default=datetime.now)

    class Meta:
        verbose_name = _('Comment Options')
        verbose_name_plural = _('Comment Options')

def build_tree(comment_list):
    for c in comment_list:
        # TODO: ugly n^2
        c.sons = [
                i for i in comment_list \
                if i.path.startswith(c.path) and i.level == c.level+1
            ]
    return comment_list

class CommentManager(models.Manager):
    # TODO @cache_this
    def get_count_for_object(self, object, **kwargs):
        target_ct = ContentType.objects.get_for_model(object)
        return self.filter(target_ct=target_ct, target_id=object.id, **kwargs).count()

    # TODO @cache_this
    def get_list_for_object(self, object, order_by=None, **kwargs):
        target_ct = ContentType.objects.get_for_model(object)
        qset = self.filter(target_ct=target_ct, target_id=object._get_pk_val(), **kwargs)
        if order_by:
            qset = qset.order_by(order_by)
        return build_tree(list(qset))

class Comment(models.Model):
    # what is this comment for
    target_ct = models.ForeignKey(ContentType, verbose_name=_('target content type'))
    target_id = models.PositiveIntegerField(_('target id'))

    # comment content
    subject = models.TextField(_('comment subject'), max_length=defaults.SUBJECT_LENGTH)
    content = models.TextField(_('comment content'), max_length=defaults.COMMENT_LENGTH)
    # comment picture
#    image = models.ImageField(_('image answer'), upload_to='comment_image', blank=True, null=True)

    # tree structure
    parent = models.ForeignKey('self', verbose_name=_('tree structure parent'), blank=True, null=True)
    path = models.CharField(_('genealogy tree path'), max_length=defaults.PATH_LENGTH, blank=True, editable=False)

    # author if is authorized
    user = models.ForeignKey(User, verbose_name=_('authorized author'), blank=True, null=True)
    # author otherwise
    nickname = models.CharField(_("anonymous author's nickname"), max_length=defaults.NICKNAME_LENGTH, blank=True)
    email = models.EmailField(_('authors email (optional)'), blank=True)
    # authors ip address
    ip_address = models.IPAddressField(_('ip address'), blank=True, null=True)

    # comment metadata
    submit_date = models.DateTimeField(_('date/time submitted'), default=datetime.now, editable=True)
    is_public = models.BooleanField(_('is public'), default=True)

    objects = CommentManager()

    @property
    def level(self):
        return len(self.path.split('/'))

    @property
    def is_authorized(self):
        if self.user_id:
            return True
        return False

    @property
    def author(self):
        if self.is_authorized:
            user = get_cached_object(User, pk=self.user_id)
            return user.username
        return self.nickname

    @property
    def is_thread_root(self):
        return self.path == ''

    @property
    def target(self):
        return get_cached_object(self.target_ct, pk=self.target_id)

    def get_genealogy_path(self):
        """genealogy tree structure field"""
        if self.parent and self.id:
            return '%s%s%d' % (self.parent.path, defaults.PATH_SEPARATOR, self.id)
        elif self.id:
            return '%d' % self.id
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
        ordering = ('-path',)
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


# initialization
from ella.comments import register
del register

