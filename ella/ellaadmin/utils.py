from django.utils.functional import memoize
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.sites.models import Site


_admin_root_cache = {} # maps model to admin url
ADMIN_NAME = 'admin'
ADMIN_SCHEME = 'http'

def admin_root(model):
    """return admin list url"""
    try:
        root = reverse(ADMIN_NAME, args=['']).strip('/')
        root = root and '/%s' % root or root
    except NoReverseMatch:
        try:
            root = '%s://%s' % (ADMIN_SCHEME, Site.objects.get(name=ADMIN_NAME).domain)
        except Site.DoesNotExist:
            root = ''
    app_label = model._meta.app_label
    model_name = model._meta.module_name
    return '%s/%s/%s' % (root, app_label, model_name)
admin_root = memoize(admin_root, _admin_root_cache, 1)

def admin_url(obj):
    """return valid admin edit page url"""
    root = admin_root(obj.__class__)
    return '%s/%d/' % (root, obj._get_pk_val())

