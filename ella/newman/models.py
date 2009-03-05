from time import time
import logging

from django.db import models, connection
from django.db.models import Q, query, ForeignKey, ManyToManyField
from django.utils.translation import ugettext_lazy as _, ugettext
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Group, Permission
from django.conf import settings

from ella.core.cache.utils import CachedForeignKey, cache_this
from ella.core.models import Category
from ella.newman.managers import DenormalizedCategoryUserRoleManager

CACHE_TIMEOUT = 10 * 60
log = logging.getLogger('ella.newman.models')

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
        unique_together = (('ct', 'field',),)


class AdminUserDraft(models.Model):
    """Here is auto-saved objects and user templates."""

    ct = CachedForeignKey(ContentType, verbose_name=_('Model'))
    user = CachedForeignKey(User, verbose_name=_('User'))
    data = models.TextField(_('Data')) # TODO: JSONField

    # If it's template, some info about it
    title = models.CharField(_('Title'), max_length=64, blank=True)
    slug = models.SlugField(_('Slug'), max_length=64, blank=True)

    is_template = models.BooleanField(_('Is template'), default=False)
    ts = models.DateTimeField(editable=False, auto_now_add=True)

    def __unicode__(self):
        if self.is_template:
            return self.title
        return "Autosaved %s (%s)" % (self.ct, self.ts)

    class Meta:
        verbose_name = _('Draft item')
        verbose_name_plural = _('Draft items')


class AdminSetting(models.Model):
    """Custom settings for newman users/groups"""

    user = CachedForeignKey(User, verbose_name=_('User'), null=True, blank=True)
    group = CachedForeignKey(Group, verbose_name=_('Group'), null=True, blank=True)
    var = models.SlugField(_('Variable'), max_length=64)
    val = models.TextField(_('Value')) # TODO: JSONField with validation...

    def __unicode__(self):
        return u"%s: %s for %s" % (self.var, self.val, self.user)

    class Meta:
        unique_together = (('user','var',),('group', 'var',), )
        verbose_name = _('Admin user setting')
        verbose_name_plural = _('Admin user settings')


class AdminGroupFav(models.Model):
    """Admin favorite items per group (presets)."""

    ct = CachedForeignKey(ContentType, verbose_name=_('Model'))
    group = CachedForeignKey(Group, verbose_name=_('Group'))
    ordering = models.PositiveSmallIntegerField(_('Ordering'))

    def __unicode__(self):
        return "%s - %s" % (self.group, self.ct)

    class Meta:
        unique_together = (('ct', 'group',),)
        ordering = ('ordering',)
        verbose_name = _('Group fav item')
        verbose_name_plural = _('Group fav items')


class AdminUserFav(models.Model):
    """Admin favorite items per user."""

    ct = CachedForeignKey(ContentType, verbose_name=_('Model'))
    user = CachedForeignKey(User, verbose_name=_('User'))
    ordering = models.PositiveSmallIntegerField(_('Ordering'))

    def __unicode__(self):
        return "%s - %s" % (self.user, self.ct)

    class Meta:
        unique_together = (('ct', 'user',),)
        ordering = ('ordering',)
        verbose_name = _('User fav item')
        verbose_name_plural = _('User fav items')


# ------------------------------------
# Permissions per Category
# ------------------------------------

# cache keys
def key_applicable_categories(func, user, permission=None):
    if not permission:
        return 'ella.newman.models.applicable_categories_%d' % user.pk
    return 'ella.newman.models.applicable_categories_%d__perm_%s' % (user.pk, permission)

def key_has_category_permission(func, user, category, permission):
    return 'ella.newman.models.has_category_permission_%d_%d__perm_%s' % (user.pk, category.pk, permission)

def key_has_model_list_permission(func, user, model):
    return 'ella.newman.models.has_model_list_permission_%d__model_%s' % (user.pk, str(model))

class CategoryUserRole(models.Model):
    """
    Apply all group's permission for the given user to this category.
    """
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    category = models.ManyToManyField(Category)

    def __unicode__(self):
        return ugettext(u'User %(user)s is a "%(group)s" for %(category)s.') % {
                'user' : self.user,
                'group' : self.group,
                'category' : [ x['slug'] for x in self.category.values() ],
            }

    def save(self):
        super(CategoryUserRole, self).save()
        self.sync_denormalized()

    def sync_denormalized(self):
        for p in self.group.permissions.all():
            code = '%s.%s' % (p.content_type.app_label, p.codename)
            cats = compute_applicable_categories(self.user, code)
            for c in cats:
                existing = DenormalizedCategoryUserRole.objects.filter(
                    contenttype_id=p.content_type.pk,
                    user_id=self.user.pk,
                    permission_codename=code,
                    category_id=c
                )
                if existing:
                    continue
                d = DenormalizedCategoryUserRole(
                    contenttype_id=p.content_type.pk,
                    user_id=self.user.pk,
                    permission_codename=code,
                    permission_id=p.pk,
                    category_id=c
                )
                d.save()

    class Meta:
        verbose_name = _("User role in category")
        verbose_name_plural = _("User roles in categories")

class DenormalizedCategoryUserRole(models.Model):
    """ for better performance """
    user_id = models.IntegerField()
    permission_id = models.IntegerField()
    permission_codename = models.CharField(max_length=100)
    category_id = models.IntegerField()
    contenttype_id = models.IntegerField()

    objects = DenormalizedCategoryUserRoleManager()

    class Meta:
        unique_together = ('user_id', 'permission_codename', 'permission_id', 'category_id', 'contenttype_id')

#@cache_this(key_has_model_list_permission, timeout=CACHE_TIMEOUT)
def has_model_list_permission(user, model):
    """ returns True if user has permission to access this model in newman, otherwise False """
    # this function takes cca 0.6-7msec both variants (CategoryUserRole or by querying denormalized schema)
    ct = ContentType.objects.get_for_model(model)
    #qs = CategoryUserRole.objects.filter(user=user, group__permissions__content_type=ct)
    qs = DenormalizedCategoryUserRole.objects.filter(user_id=user.id, contenttype_id=ct.pk).distinct()
    if qs.count():
        return True
    return False

#@cache_this(key_has_category_permission, timeout=CACHE_TIMEOUT)
def has_category_permission(user, category, permission):
    if user.has_perm(permission):
        return True

    #takes 0.5..2 msec
    if type(permission) in [list, tuple]:
        qs = DenormalizedCategoryUserRole.objects.filter(
            user_id=user.pk,
            permission_codename__in=permission,
            category_id=category.pk
        )
    else:
        qs = DenormalizedCategoryUserRole.objects.filter(
            user_id=user.pk,
            permission_codename=permission,
            category_id=category.pk
        )
    if qs.count():
        return True
    return False

def has_object_permission(user, obj, permission):
    if user.has_perm(permission):
        return True
    ct = ContentType.objects.get_for_model(obj)
    if type(permission) in [list, tuple]:
        qs = DenormalizedCategoryUserRole.objects.filter(
            user_id=user.pk,
            permission_codename__in=permission,
            contenttype_id=ct.pk
        )
    else:
        qs = DenormalizedCategoryUserRole.objects.filter(
            user_id=user.pk,
            permission_codename=permission,
            contenttype_id=ct.pk
        )
    if model_category_fk(obj):
        qs = qs.filter( category_id=model_category_fk_value(obj).pk )
    if qs.count():
        return True
    return False

def category_children(cats):
    """
    Returns all nested categories as list.
    @param cats: list of Category objects
    """
    sub_cats = map(None, cats)
    for c in cats:
        out = Category.objects.filter(tree_parent=c)
        map(lambda o: sub_cats.append(o), category_children(out))
    return sub_cats

#@cache_this(key_applicable_categories, timeout=CACHE_TIMEOUT)
def compute_applicable_categories(user, permission=None):
    """ Return categories accessible by given user """
    if user.is_superuser:
        all = Category.objects.all()
        return [ d.pk for d in all ]

    category_user_roles = CategoryUserRole.objects.filter(user=user).distinct()
    if permission:
        app_label, code = permission.split('.', 1)
        perms = Permission.objects.filter(content_type__app_label=app_label, codename=code)
        if not perms:
            # no permission found (maybe misspeled) then no categories permitted!
            log.warning('No permission [%s] found for user %s' % (permission, user.username))
            return []
        category_user_roles = category_user_roles.filter(group__permissions=perms[0])
    else:
        # take any permission
        category_user_roles = category_user_roles.filter(group__permissions__id__isnull=False)

    unique_categories = set()
    for category_user_role in category_user_roles:
        for category in category_user_role.category.all():
            unique_categories.add(category)
    app_cats = category_children(unique_categories)
    return [ d.pk for d in app_cats ]

def applicable_categories(user, permission=None):
    # takes approx. 5-16msec , old version took 250+ msec
    if user.is_superuser:
        all = Category.objects.all()
        return [ d.pk for d in all ]
    if permission:
        return DenormalizedCategoryUserRole.objects.categories_by_user_and_permission(user, permission)
    else:
        return DenormalizedCategoryUserRole.objects.categories_by_user(user)
    return map(lambda x: x.category_id, qs)

def permission_filtered_model_qs(queryset, user, permissions=[]):
    """ returns Queryset filtered accordingly to given permissions """
    if user.is_superuser:
        return queryset
    q = queryset
    qs = query.EmptyQuerySet()
    if 'category' in queryset.model._meta.get_all_field_names():
        categories = DenormalizedCategoryUserRole.objects.categories_by_user_and_permission(user, permissions)
        if categories:
            if queryset.model == Category:
                qs = q.filter( pk__in=categories )
            else:
                qs = q.filter( category__in=categories )
    return qs

def is_category_fk(db_field):
    if not isinstance(db_field, (ForeignKey, ManyToManyField)):
        return False
    rel_ct = ContentType.objects.get_for_model(db_field.rel.to)
    if rel_ct == ContentType.objects.get_for_model(Category):
        return True
    return False

def model_category_fk_value(model):
    """ returns value of field related to Category """
    if not model:
        return None
    for f in model._meta.fields:
        if is_category_fk(f):
            return getattr(model, f.name)
    return None

def model_category_fk(model):
    """ returns model's field related to Category """
    if not model:
        return None
    for f in model._meta.fields:
        if is_category_fk(f):
            return f
    return None

def get_permission(permission_name, instance):
    return instance._meta.app_label + '.' + '%s_' % permission_name + instance._meta.module_name.lower()

def generate_test_data(filepath='/home/jonson/src/nc/ella/ella/newman/testbed/service/fixtures/test_data.yaml'):
    from django.contrib.sites.models import Site
    from django.core.serializers import serialize
    FMT = 'yaml'
    #data = list(ContentType.objects.all()) + list(Category.objects.all()) + list(Site.objects.all())
    data = list(Permission.objects.all())
    file(filepath, 'w').write( serialize(FMT, data) )

