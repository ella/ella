import sys
import logging
from time import time
import traceback
import anyjson

from django.http import HttpResponse
from django.contrib.admin.models import LogEntry
from django.db.models.aggregates import Max
from django.core.urlresolvers import reverse

from ella.newman import models
from ella.newman.conf import newman_settings
from ella.core.models import Category

log = logging.getLogger('ella.newman')


class Profiler:
    "Provides measurement of time spent in named blocks of code."
    def __init__(self):
        self.timers = []

    def create_timer(self, name):
        t = ProfilerTimer(name)
        self.timers.append(t)
        return t

    def create_started_timer(self, name):
        t = self.create_timer(name)
        t.start()
        return t

    def log_summary(self, logger_callback):
        total = 0.0
        for t in self.timers:
            logger_callback(
                '%05.03f msec elapsed in %s' %
                (
                    t.get_msec(),
                    t.name,
                )
            )
            total += t.get_msec()
        logger_callback('TOTAL: %05.03f msec.' % total)

    @property
    def has_data(self):
        return len(self.timers) > 0

    def reset(self):
        for i in range(len(self.timers)):
            self.timers.pop()

# this instance should be used for creating timers and profiling blocks of code
PROFILER = Profiler()

class ProfilerTimer:
    "Measures one named block of code."
    def __init__(self, name):
        self.name = name
        self.elapsed_time = 0.0
        self.begin = 0.0

    def get_sec(self):
        return self.elapsed_time

    def get_msec(self):
        return self.elapsed_time * 1000

    def start(self):
        if self.begin:
            raise AttributeError('Timer already started!')
        self.begin = time()

    def stop(self):
        if not self.begin:
            raise AttributeError('Timer not started!')
        self.elapsed_time = time() - self.begin

def profiled_section(func):
    def decorated(*args, **kwargs):
        trac = traceback.extract_stack()[-2]
        caller = '[%s] (%s:%d)' % (trac[2], trac[0], trac[1])
        name = '[%s] called from %s' % (func.__name__, caller)
        prof = PROFILER.create_started_timer(name)
        out = func(*args, **kwargs)
        prof.stop()
        return out
    return decorated

def json_encode(data):
    """ Encode python data into JSON. Try faster cjson first. """

    return anyjson.serialize(data)

def json_decode(str):
    """ Decode JSON string into python. """

    return anyjson.deserialize(str)

def JsonResponse(message, data={}, errors={}, status=newman_settings.STATUS_OK, http_status=newman_settings.HTTP_OK):
    """ Return JSON response in newman's standard format. """

    out_dict = {
        'status': status,
        'message': message,
    }
    if data:
        # if data contains JSON data, first try to decode them
        if isinstance(data, (str, unicode)):
            try:
                data = json_decode(data)
            except ValueError, e:
                log.info('%s, data=[%s]' % (e, data))

        out_dict['data'] = data
    if errors:
        http_status = 405
        out_dict['errors'] = errors
    out = json_encode(out_dict)
    return HttpResponse(out, mimetype='text/plain;charset=utf-8', status=http_status)

def JsonResponseError(message, status=newman_settings.STATUS_GENERIC_ERROR):
    """ use this function if one message describes error well, so  """
    return JsonResponse(message, status=status, http_status=newman_settings.HTTP_ERROR)

def JsonResponseRedirect(location):
    " Returns HTTP 200 response containing JSON dict with redirect_to field. "
    out_dict = {
        'status': newman_settings.STATUS_JSON_REDIRECT,
        'redirect_to': location
    }
    out = json_encode(out_dict)
    response = HttpResponse(out, mimetype='text/plain;charset=utf-8', status=newman_settings.HTTP_OK)
    response['Redirect-To'] = location
    return response

def decode_category_filter_json(data):
    decoded = json_decode(data)
    return map(lambda cid: int(cid), decoded)

def set_user_config(user, key, value):
    """ sets user defined configuration to  user.config and to session as well. """
    if not hasattr(user, newman_settings.USER_CONFIG):
        setattr(user, newman_settings.USER_CONFIG, {})
    cfg = getattr(user, newman_settings.USER_CONFIG)
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
    if newman_settings.USER_CONFIG not in session:
        session[newman_settings.USER_CONFIG] = dict()
    conf = session[newman_settings.USER_CONFIG]
    callback = _get_decoder(key)
    if not callback:
        conf[key] = value
    else:
        # As there is JSON decode callback, keep data in session decoded.
        conf[key] = callback(json_encode(value))
    session[key] = conf

def _get_decoder(key):
    for k, v in newman_settings.JSON_CONVERSIONS:
        if k == key:
            return getattr(sys.modules[__name__], v)

def get_user_config(user, key):
    """
    Returns user defined configuration from user.config with fallback to AdminSetting.

    If AdminSetting is reached data_decode_callback is used to transform saved data
    from JSON to proper format (i.e. all list items convert to int). Default
    data_decode_callback only decodes data from JSON.
    """
    cfg = getattr(user, newman_settings.USER_CONFIG, {})
    if key not in cfg:
        try:
            db_data = models.AdminSetting.objects.get(user=user, var=key)
        except models.AdminSetting.DoesNotExist:
            return None
        # find appropriate callback to convert JSON data.
        callback = _get_decoder(key)
        if not callback:
            callback = json_decode
        return callback(db_data.value)
    return cfg[key]

def flag_queryset(queryset, flag, value):
    if not hasattr(queryset, '_filter_flags'):
        setattr(queryset, '_filter_flags', dict())
    queryset._filter_flags[flag] = value

def get_queryset_flag(queryset, flag):
    if not hasattr(queryset, '_filter_flags'):
        return False
    return queryset._filter_flags.get(flag, False)

def copy_queryset_flags(qs_dest, qs_src):
    setattr(qs_dest, '_filter_flags', getattr(qs_src, '_filter_flags', {}))

def user_category_filter(queryset, user):
    """
    Returns Queryset containing only user's prefered content (filtering based on categories).
    If queryset.model has no relation to ella.core.models.Category, original queryset is returned.
    """
    from ella.newman.permission import model_category_fk, is_category_model
    qs = queryset
    category_fk = model_category_fk(qs.model)
    if not category_fk:
        return qs
    root_category_ids = get_user_config(user, newman_settings.CATEGORY_FILTER)
    if not root_category_ids: # user has no custom category filter set or his filter set is empty.
        return qs
    if not user.is_superuser:
        helper = models.DenormalizedCategoryUserRole.objects.filter(
            user_id=user.pk,
            root_category_id__in=root_category_ids
        ).values('category_id')
        user_categories = [c['category_id'] for c in helper]
        if is_category_model(qs.model):
            lookup = 'id__in'
        else:
            lookup = '%s__in' % category_fk.name
        out = qs.filter(**{lookup: user_categories})
    else:
        cats = Category.objects.filter(pk__in=root_category_ids).values('site__pk')
        user_sites = [c['site__pk'] for c in cats]
        if is_category_model(qs.model):
            lookup = 'site__id__in'
        else:
            lookup = '%s__site__id__in' % category_fk.name
        out = qs.filter(**{lookup: user_sites})
    flag_queryset(out, 'user_category_filtered', True)
    return out

def is_user_category_filtered(queryset):
    return get_queryset_flag(queryset, 'user_category_filtered')

def get_log_entries(limit=15, filters={}):
    entry_ids = LogEntry.objects.values('object_id', 'content_type_id').annotate(last_edit=Max('action_time'), max_id=Max('id')).filter(**filters).order_by('-last_edit')[:limit]
    return LogEntry.objects.filter(pk__in=[i['max_id'] for i in entry_ids])

# newman url for object for other apps, FEs...
def get_newman_url(obj):
    """return valid admin edit page url"""
    model = obj.__class__
    info = model._meta.app_label, model._meta.module_name
    return reverse('newman:%s_%s_change' % info, args=(obj._get_pk_val(),))
