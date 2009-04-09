import sys
import logging
try:
    import cjson
    dumps = cjson.encode
    loads = cjson.decode
except ImportError:
    from django.utils.simplejson import dumps, loads

from django.http import HttpResponse
from ella.newman.permission import model_category_fk
from ella.newman import models
from ella.newman.config import STATUS_OK, STATUS_GENERIC_ERROR
from ella.newman.config import CATEGORY_FILTER, USER_CONFIG, JSON_CONVERSIONS
from ella.core.models import Category

log = logging.getLogger('ella.newman')

def json_encode(data):
    """ Encode python data into JSON. Try faster cjson first. """

    return dumps(data)

def json_decode(str):
    """ Decode JSON string into python. """

    return loads(str)

def JsonResponse(message, data={}, errors={}, status=STATUS_OK):
    """ Return JSON response in newman's standard format. """

    out_dict = {
        'status': status,
        'message': message,
    }
    http_status = 200
    if data:
        try: 
            data = json_encode(data)
        except: 
            http_status = 405
            log.error('Cannot decode json data in JsonResponse(), data=[%s]' % data)
        
        out_dict['data'] = data
    if errors:
        http_status = 405
        out_dict['errors'] = errors
    out = json_encode(out_dict)
    return HttpResponse(out, mimetype='text/plain;charset=utf-8', status=http_status)

def JsonResponseError(message, status=STATUS_GENERIC_ERROR):
    """ use this function if one message describes error well, so  """
    err_dict = {'error_description': message}
    return JsonResponse(message, errors=err_dict, status=status)

def decode_category_filter_json(data):
    decoded = json_decode(data)
    return map(lambda cid: int(cid), decoded)

def set_user_config(user, key, value):
    """ sets user defined configuration to  user.config and to session as well. """
    if not hasattr(user, USER_CONFIG):
        setattr(user, USER_CONFIG, {})
    cfg = getattr(user, USER_CONFIG)
    cfg[key] = value

def set_user_config_db(user, key, value):
    # set AdminSetting data
    obj, status = models.AdminSetting.objects.get_or_create(
        user = user,
        var = key
    )
    obj.val = '%s' % json_encode(value)
    obj.save()

def set_user_config_session(session, key, value):
    # set session data
    if USER_CONFIG not in session:
        session[USER_CONFIG] = dict()
    conf = session[USER_CONFIG]
    callback = _get_decoder(key)
    if not callback:
        conf[key] = value
    else:
        # As there is JSON decode callback, keep data in session decoded.
        conf[key] = callback(json_encode(value))
    session[key] = conf

def _get_decoder(key):
    for k, v in JSON_CONVERSIONS:
        if k == key:
            return getattr(sys.modules[__name__], v)

def get_user_config(user, key):
    """
    Returns user defined configuration from user.config with fallback to AdminSetting.

    If AdminSetting is reached data_decode_callback is used to transform saved data
    from JSON to proper format (i.e. all list items convert to int). Default
    data_decode_callback only decodes data from JSON.
    """
    cfg = getattr(user, USER_CONFIG, {})
    if key not in cfg:
        db_data = models.AdminSetting.objects.filter(user=user, var=key)
        if not db_data:
            return None
        # find appropriate callback to convert JSON data.
        callback = _get_decoder(key)
        if not callback:
            callback = json_decode
        return callback(db_data[0].value)
    return cfg[key]

def user_category_filter(queryset, user):
    """
    Returns Queryset containing only user's prefered content (filtering based on categories).
    If queryset.model has no relation to ella.core.models.Category, original queryset is returned.
    """
    qs = queryset
    category_fk = model_category_fk(qs.model)
    if not category_fk:
        return qs
    root_category_ids = get_user_config(user, CATEGORY_FILTER)
    if not root_category_ids: # user has no custom category filter set or his filter set is empty.
        return qs
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
