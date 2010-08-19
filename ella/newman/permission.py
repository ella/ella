"""
Category based permission handling functions.
These should be used by other modules rather than accessing
CategoryUserRole objects.
"""
import logging

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.contrib.sites.models import Site
from django.db.models import query, ForeignKey, ManyToManyField

from ella.core.models import Category
from ella.newman.models import CategoryUserRole, DenormalizedCategoryUserRole

CACHE_TIMEOUT = 10 * 60
log = logging.getLogger('ella.newman.models')

# cache keys
def key_applicable_categories(func, user, permission=None):
    if not permission:
        return 'ella.newman.permission.applicable_categories_%d' % user.pk
    return 'ella.newman.permission.applicable_categories_%d__perm_%s' % (user.pk, permission)

def key_has_category_permission(func, user, category, permission):
    return 'ella.newman.permission.has_category_permission_%d_%d__perm_%s' % (user.pk, category.pk, permission)

def key_has_model_list_permission(func, user, model):
    return 'ella.newman.permission.has_model_list_permission_%d__model_%s' % (user.pk, str(model))

#@cache_this(key_has_model_list_permission, timeout=CACHE_TIMEOUT)
#@utils.profiled_section
def has_model_list_permission(user, model):
    """ returns True if user has permission to access this model in newman, otherwise False """
    if user.is_superuser:
        return True
    # this function takes cca 0.6-7msec both variants (CategoryUserRole or by querying denormalized schema)
    ct = ContentType.objects.get_for_model(model)
    #qs = CategoryUserRole.objects.filter(user=user, group__permissions__content_type=ct)
    qs = DenormalizedCategoryUserRole.objects.filter(user_id=user.id, contenttype_id=ct.pk).distinct()
    return qs.count() > 0

#@cache_this(key_has_category_permission, timeout=CACHE_TIMEOUT)
#@utils.profiled_section
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

#@utils.profiled_section
def has_object_permission(user, obj, permission):
    """
    Return whether user has given permission for given object,
    either through standard Django permission, or via permission
    to any category that object is placed in.
    """
    ct = ContentType.objects.get_for_model(obj)
    if user.has_perm(permission):
        additional = DenormalizedCategoryUserRole.objects.filter(
            user_id=user.pk,
            contenttype_id=ct.pk
        )
        # user has permission and hasn't any existing role to obj's content type
        if additional.count() == 0:
            return True
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

#@utils.profiled_section
def category_children(cats):
    """
    Returns all nested categories as list.
    @param cats: list of Category objects
    """
    sub_cats = set(map(None, cats))
    for c in cats:
        out = Category.objects.filter(tree_parent=c)
        map(lambda o: sub_cats.add(o), category_children(out))
    return sub_cats

#@cache_this(key_applicable_categories, timeout=CACHE_TIMEOUT)
#@utils.profiled_section
def compute_applicable_categories_objects(user, permission=None):
    """ Return categories accessible by given user """
    if user.is_superuser:
        #all = Category.objects.all().values('id')
        #return [ d['id'] for d in all ]
        all = Category.objects.select_related().all()
        return [ d for d in all ]

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
        for category in category_user_role.category.select_related().all():
            unique_categories.add(category)
    app_cats = category_children(unique_categories)
    return app_cats

#@utils.profiled_section
def compute_applicable_categories(user, permission=None):
    categories = compute_applicable_categories_objects(user, permission)
    return list(d.pk for d in categories)

#@utils.profiled_section
def applicable_categories(user, permission=None):
    """
    Return list of categories accessible for given permission.
    Use denormalized values.
    """
    # takes approx. 5-16msec , old version took 250+ msec
    if user.is_superuser:
        all = Category.objects.all().values('id')
        return [ d['id'] for d in all ]
    if permission:
        return DenormalizedCategoryUserRole.objects.categories_by_user_and_permission(user, permission)
    else:
        return DenormalizedCategoryUserRole.objects.categories_by_user(user)

#@utils.profiled_section
def permission_filtered_model_qs(queryset, user, permissions=[]):
    """ returns Queryset filtered accordingly to given permissions """
    if user.is_superuser:
        return queryset
    category_fk = model_category_fk(queryset.model)
    if not category_fk:
        return queryset
    q = queryset
    qs = query.EmptyQuerySet()
    if permissions:
        categories = DenormalizedCategoryUserRole.objects.categories_by_user_and_permission(user, permissions)
    else:
        categories = DenormalizedCategoryUserRole.objects.categories_by_user(user)
    if categories:
        if queryset.model == Category:
            qs = q.filter( pk__in=categories )
        else:
            lookup = '%s__in' % category_fk.name
            qs = q.filter(**{lookup: categories})
    return qs

def is_category_fk(db_field):
    """
    Return wheter given database field is ForeignKey pointing to Category
    """
    if not isinstance(db_field, (ForeignKey, ManyToManyField)):
        return False
    return db_field.rel.to == Category

def is_site_fk(db_field):
    """
    Return wheter given database field is ForeignKey pointing to Site
    """
    if not isinstance(db_field, (ForeignKey, ManyToManyField)):
        return False
    return db_field.rel.to == Site

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
    fk_list = []
    for f in model._meta.fields:
        if is_category_fk(f):
            fk_list.append(f)
    if not fk_list:
        return None
    for fk in fk_list:
        # fields named 'category' have higher priority
        if fk.name.lower() == 'category':
            return fk
    return fk_list[0]

def is_category_model(model):
    return model == Category

def get_permission(permission_name, instance):
    return instance._meta.app_label + '.' + '%s_' % permission_name + instance._meta.module_name.lower()

