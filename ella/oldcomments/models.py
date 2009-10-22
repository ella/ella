from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_str

from ella.core.cache.invalidate import CACHE_DELETER
from ella.core.cache.utils import get_cached_object, CachedGenericForeignKey
from ella.ellaadmin.utils import admin_url

from ella.oldcomments import defaults


class CommentOptions(models.Model):
    """contains comment options string for object"""
    target_ct = models.ForeignKey(ContentType, verbose_name=_('Target content type'))
    target_id = models.PositiveIntegerField(_('Target id'))
    target = CachedGenericForeignKey(ct_field="target_ct", fk_field="target_id")
    # TODO: options should not be string but boolean columns
    options = models.CharField(max_length=defaults.OPTS_LENGTH, blank=True)
    timestamp = models.DateTimeField(default=datetime.now)

    class Meta:
        db_table = 'comments_commentoptions'
        verbose_name = _('Comment Options')
        verbose_name_plural = _('Comment Options')

def build_tree(comment_list):
    """create nested comments"""
    for c in comment_list:
        # ugly n^2
        c.sons = [
                i for i in comment_list \
                if i.path.startswith(c.path) and i.level == c.level+1
            ]
    return comment_list

def get_key(object, type, **kwargs):
    if kwargs:
        kw = ','.join(':'.join((key, smart_str(kwargs[key]))) for key in sorted(kwargs.keys()))
    else:
        kw = ''
    return 'ella.comments.models.CommentManager.get_%s_for_object:%s:%s:%d:%s' % (
            type,
            object._meta.app_label,
            object._meta.object_name,
            object.pk,
            kw
    )

def get_count_key(func, self, object, **kwargs):
    return get_key(object, 'count', **kwargs)

def get_list_key(func, self, object, **kwargs):
    return get_key(object, 'list', **kwargs)

def invalidate_cache(key,  self, object, **kwargs):
    target_ct = ContentType.objects.get_for_model(object)
    CACHE_DELETER.register_test(Comment, "target_id:%s;target_ct_id:%s" % (object.pk, target_ct.pk) , key)

class CommentManager(models.Manager):
    def get_count_for_object(self, object, **kwargs):
        target_ct = ContentType.objects.get_for_model(object)
        return self.filter(target_ct=target_ct, target_id=object.id, **kwargs).count()

    def get_list_for_object(self, object, order_by=None, limit=None, **kwargs):
        target_ct = ContentType.objects.get_for_model(object)
        qset = self.filter(target_ct=target_ct, target_id=object.pk, **kwargs)
        if order_by:
            qset = qset.order_by(order_by)
        if limit:
            qset = qset[:limit]
        return build_tree(list(qset))

class Comment(models.Model):
    """generic comments' model """
    # what is this comment for
    target_ct = models.ForeignKey(ContentType, verbose_name=_('Target content type'))
    target_id = models.PositiveIntegerField(_('Target id'))

    target = CachedGenericForeignKey(ct_field="target_ct", fk_field="target_id")

    # comment content
    subject = models.TextField(_('Comment subject'), max_length=defaults.SUBJECT_LENGTH)
    content = models.TextField(_('Comment content'), max_length=defaults.COMMENT_LENGTH)
    # comment picture
    #image = models.ImageField(_('Image answer'), upload_to='comment_image', blank=True, null=True)

    # tree structure
    parent = models.ForeignKey('self', verbose_name=_('Tree structure parent'), blank=True, null=True)
    path = models.CharField(_('Genealogy tree path'), max_length=defaults.PATH_LENGTH, blank=True, editable=False)

    # authorized author
    user = models.ForeignKey(User, verbose_name=_('Authorized author'), blank=True, null=True)
    # anonymous author
    nickname = models.CharField(_("Anonymous author's nickname"), max_length=defaults.NICKNAME_LENGTH, blank=True)
    email = models.EmailField(_('Authors email (optional)'), blank=True)
    # author's ip address
    ip_address = models.IPAddressField(_('IP address'), blank=True, null=True)

    # comment metadata
    submit_date = models.DateTimeField(_('Time submitted'), default=datetime.now, editable=True)
    is_public = models.BooleanField(_('Is public'), default=True)

    objects = CommentManager()

    @property
    def level(self):
        return len(self.path.split(defaults.PATH_SEPARATOR))

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

    def get_genealogy_path(self):
        """genealogy tree structure field"""
        if self.parent and self.id:
            return '%s%s%d' % (self.parent.path, defaults.PATH_SEPARATOR, self.id)
        elif self.id:
            return '%d' % self.id
        return ''

    def get_admin_url(self):
        return admin_url(self)

    def save(self, **kwargs):
        # TODO: maybe create models.GenealogyField for this
        # first save to obtain primary key
        super(Comment, self).save(**kwargs)
        # This can raise "Forced update did not affect any rows" exception
#        force_insert, force_update = False, True
        # do not store too long path
        path = self.get_genealogy_path()
        if len(path) <= defaults.PATH_LENGTH:
            self.path = path
        else:
            self.path = self.parent.path
        # save it all
        super(Comment, self).save(**kwargs)

    def __unicode__(self):
        if self.id:
            return u"comment [id:%d] '%s...' on %s {path:%s}" % (self.id, self.content[:10],
                    self.target, self.path)
        return u"unsaved comment"

    class Meta:
        db_table = 'comments_comment'
        ordering = ('-path',)
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')


class BannedUser(models.Model):
    """
    model with generic relation on object
    same as in comment model
    ban is global if there is no relation
    """
    target_ct = models.ForeignKey(ContentType, verbose_name=_('Target content type'))
    target_id = models.PositiveIntegerField(_('Target id'))
    user = models.ForeignKey(User, verbose_name=_('Banned author'))

    target = CachedGenericForeignKey(ct_field="target_ct", fk_field="target_id")

    class Meta:
        db_table = 'comments_banneduser'
        verbose_name = _('Banned User')
        verbose_name_plural = _('Banned Users')


class BannedIP(models.Model):
    pass
    class Meta:
        db_table = 'comments_bannedip'

