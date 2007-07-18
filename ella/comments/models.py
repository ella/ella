from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from ella.comments import defaults

from datetime import datetime


class CommentOptions(models.Model):
    """
    contains options string for discussion
    with immediate effect
    """
    target_ct = models.ForeignKey(ContentType)
    target_id = models.PositiveIntegerField()
    options = models.CharField(maxlength=defaults.OPTS_LENGTH, blank=True)
    timestamp = models.DateTimeField(default=datetime.now)

    class Admin:
        pass

class Comment(models.Model):
    # what is this comment for
    target_ct = models.ForeignKey(ContentType, verbose_name=_('target content type'))
    target_id = models.PositiveIntegerField(_('target id'))

    # comment content
    content = models.TextField(_('comment content'), maxlength=defaults.COMMENT_LENGTH)
    # comment picture
#    image = models.ImageField(_('image answer'), upload_to='comment_image', blank=True, null=True)

    # tree structure
    parent = models.ForeignKey('self', verbose_name=_('tree structure parent'), blank=True, null=True)
    path = models.CharField(_('genealogy tree path'), maxlength=defaults.PATH_LENGTH, editable=True)

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

    def as_html(self):
        """returns html repr of this comment"""
        if self.user:
            author = self.user.username
            author += ' - authorized'
        else:
            author = self.nickname
            author += ' - NOT authorized'
        html = '\n'.join((
            '<div id="nc_comments_%d">',
            '<p>author: %s</p>',
            '<p>submit: %s</p>',
            '<p>%s</p>',
            '<hr />',
            '</div>',
)) % (self.id, author, self.submit_date, self.content)

        return html


    def get_genealogy_path(self, parent=None):
        """genealogy tree structure field"""
        if parent:
            return '%s%x%s' % (parent.path, parent.id, defaults.PATH_SEPARATOR)
        else:
            return defaults.PATH_SEPARATOR

    def save(self):
        # TODO: create models.GenealogyField for this
        path = self.get_genealogy_path(self.parent)
        if len(path) <= defaults.PATH_LENGTH:
            self.path = self.get_genealogy_path(self.parent)
        else:
            self.path = parent.path
        super(Comment, self).save()

    def __unicode__(self):
        if self.id:
            return u"comment[%d] '%s ...' on %s {path:%s}" % (self.id, self.content[:10],
                    self.target_ct.get_object_for_this_type(pk=self.target_id), self.path)
        else:
            return u"unsaved comment"

    class Admin:
        pass


class BannedUser(models.Model):
    """
    model with generic relation on object - same as in comment model
    ban is global if there is no relation
    """
    target_ct = models.ForeignKey(ContentType)
    target_id = models.PositiveIntegerField()
    user = models.ForeignKey(User)

    class Admin:
        pass



# Register the admin options for these models.


from django import VERSION
from django.contrib import admin

admin.site.register(Comment)
admin.site.register(BannedUser)
admin.site.register(CommentOptions)


