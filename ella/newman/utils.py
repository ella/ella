try:
    import cjson
    dumps = cjson.encode
    loads = cjson.decode
except ImportError:
    from django.utils.simplejson import dumps, loads

from django.contrib.sites.models import Site

from ella.newman.permission import model_category_fk
from ella.newman import models
from ella.core.models import Category
from ella.core.cache.utils import cache_this

def json_encode(data):
    """ Encode python data into JSON. Try faster cjson first. """

    return dumps(data)

def json_decode(str):
    """ Decode JSON string into python. """

    return loads(str)

def user_category_filter(queryset, user):
    """ 
    Returns Queryset containing only user's prefered content (filtering based on categories). 
    If queryset.model has no relation to ella.core.models.Category, original queryset is returned. 
    """
    qs = queryset
    category_fk = model_category_fk(qs.model)
    if not category_fk:
        return qs
    user_categories = models.AdminSetting.objects.filter(user=user, var='category_filter')
    if not user_categories: # user has no custom category filter set
        return qs
    decoded = json_decode(user_categories[0].value)
    if not decoded:
        return qs
    root_category_ids = map(lambda cid: int(cid), decoded)
    if not user.is_superuser:
        helper = models.DenormalizedCategoryUserRole.objects.filter(
            user_id=user.pk, 
            root_category_id__in=root_category_ids
        )
        user_categories = map(lambda c: c.category_id, helper)
        lookup = '%s__in' % category_fk.name
        return qs.filter(**{lookup: user_categories})
    else:
        cats = Category.objects.filter(pk__in=root_category_ids)
        user_sites = map(lambda c: c.site.pk, cats)
        lookup = '%s__site__in' % category_fk.name
        return qs.filter(**{lookup: user_sites})
