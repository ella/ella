from django.db import models, IntegrityError
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Group
from django.template.defaultfilters import date
from django.conf import settings

from ella.core.cache.utils import CachedForeignKey
from ella.core.models import Category
from ella.newman.managers import DenormalizedCategoryUserRoleManager

class DevMessage(models.Model):
    """Development news for ella administrators."""

    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=32)
    summary = models.TextField(_('Summary'))
    details = models.TextField(_('Detail'), blank=True)
    version = models.CharField(_('Version'), max_length=32)

    author = models.ForeignKey(User, editable=False)
    ts = models.DateTimeField(editable=False, auto_now_add=True)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Development message')
        verbose_name_plural = _('Development messages')
        ordering = ('-ts',)
        unique_together = (('slug', 'ts',),)


class AdminHelpItem(models.Model):
    """Help for ella administrators, that extends django help_text functionality."""

    ct = CachedForeignKey(ContentType, verbose_name=_('Model'))
    field = models.CharField(_('Field'), max_length=64, blank=True)
    lang = models.CharField(_('Language'), max_length=5, choices=settings.LANGUAGES)
    short = models.CharField(_('Short help'), max_length=255)
    long = models.TextField(_('Full message'), blank=True)

    def __unicode__(self):
        if self.field:
            return u"%s: %s" % (self.ct, self.field)
        return u"%s: %s" % (self.ct, _('General'))

    class Meta:
        verbose_name = _('Help item')
        verbose_name_plural = _('Help items')
        ordering = ('ct', 'field',)
        unique_together = (('ct', 'field', 'lang',),)


class AdminUserDraft(models.Model):
    """Here is auto-saved objects and user templates."""

    ct = CachedForeignKey(ContentType, verbose_name=_('Model'))
    user = CachedForeignKey(User, verbose_name=_('User'))
    data = models.TextField(_('Data'))

    # Preset title
    title = models.CharField(_('Title'), max_length=64, blank=True)
    ts = models.DateTimeField(editable=False, auto_now=True)

    @property
    def is_preset(self):
        return self.title != ''

    def __unicode__(self):
        if self.is_preset:
            return u"%s (%s)" % (self.title, date(self.ts, 'y-m-d H:i'))
        return u"%s %s (%s)" % (_("Autosaved"), _(self.ct.name), date(self.ts, 'y-m-d H:i'))

    class Meta:
        verbose_name = _('Draft item')
        verbose_name_plural = _('Draft items')
        ordering = ('-ts',)


class AdminSetting(models.Model):
    """Custom settings for newman users/groups"""

    user = CachedForeignKey(User, verbose_name=_('User'), null=True, blank=True)
    group = CachedForeignKey(Group, verbose_name=_('Group'), null=True, blank=True)
    var = models.SlugField(_('Variable'), max_length=64)
    val = models.TextField(_('Value'))

    def __unicode__(self):
        return u"%s: %s for %s" % (self.var, self.val, self.user)

    def __get_val(self):
        return self.val

    def __set_val(self, v):
        self.val = v
    value = property(__get_val, __set_val)

    class Meta:
        unique_together = (('user','var',),('group', 'var',), )
        verbose_name = _('Admin user setting')
        verbose_name_plural = _('Admin user settings')


# ------------------------------------
# Permissions per Category
# ------------------------------------

class CategoryUserRole(models.Model):
    """
    Apply all group's permission for the given user to this category.
    """
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    category = models.ManyToManyField(Category)

    def __unicode__(self):
        try:
            return ugettext(u'User %(user)s is a "%(group)s" for %(category)s.') % {
                    'user' : self.user,
                    'group' : self.group,
                    'category' : [ x['slug'] for x in self.category.values() ],
                }
        except ValueError, ve:
            return ugettext(u'User %(user)s is a "%(group)s" for %(category)s.') % {
                    'user' : self.user,
                    'group' : self.group,
                    'category' : 'unknown'
                }

    def save(self, *args, **kwargs):
        sync = kwargs.pop('sync_role', False)
        super(CategoryUserRole, self).save(*args, **kwargs)
        if sync:
            self.sync_denormalized()

    def sync_denormalized(self):
        from ella.newman.permission import compute_applicable_categories_objects
        denormalized = []
        cats = []
        #for p in self.group.permissions.all():
        for p in self.group.permissions.all().iterator():
            code = '%s.%s' % (p.content_type.app_label, p.codename)
            # Category list is NOT NECESSARILY identical for every permission code in CUR's group
            cats = compute_applicable_categories_objects(self.user, code)
            #print 'Denormalizing %s for %d categories' % (code, len(cats))
            # create denormalized roles
            for c in cats:
                root_cat = c.main_parent
                if not root_cat:
                    root_cat = c #c is top category
                elif root_cat.tree_parent_id:
                    root_cat = root_cat.get_tree_parent()
                try:
                    obj = DenormalizedCategoryUserRole.objects.create(
                        contenttype_id=p.content_type.pk,
                        user_id=self.user.pk,
                        permission_codename=code,
                        permission_id=p.pk,
                        category_id=c.pk,
                        root_category_id=root_cat.pk
                    )
                    denormalized.append(obj)
                except IntegrityError:
                    pass
        return denormalized

    class Meta:
        verbose_name = _("User role in category")
        verbose_name_plural = _("User roles in categories")

class DenormalizedCategoryUserRole(models.Model):
    """ for better performance """
    user_id = models.IntegerField(db_index=True)
    permission_id = models.IntegerField()
    permission_codename = models.CharField(max_length=100)
    category_id = models.IntegerField()
    root_category_id = models.IntegerField()
    contenttype_id = models.IntegerField()

    objects = DenormalizedCategoryUserRoleManager()

    class Meta:
        unique_together = ('user_id', 'permission_codename', 'permission_id', 'category_id', 'contenttype_id')

