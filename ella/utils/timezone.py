import time
import calendar
from pytz import utc
from datetime import datetime

from django.conf import settings

use_tz = getattr(settings, 'USE_TZ', False)
try:
    # try import offset-aware datetime from Django >= 1.4
    from django.utils.timezone import now, localtime, get_current_timezone, make_aware
except ImportError:
    # backward compatibility with Django < 1.4 (offset-naive datetimes)
    from datetime import datetime
    now = datetime.now
    use_tz = False


def utc_localize(dtime):
    if use_tz:
        if dtime.tzinfo:
            return utc.normalize(dtime)
        else:
            return utc.localize(dtime)
    return dtime

def localize(dtime):
    if use_tz:
        if dtime.tzinfo:
            return localtime(dtime)
        else:
            return make_aware(dtime, get_current_timezone())
    return dtime

def to_timestamp(dtime):
    if use_tz:
        return calendar.timegm(dtime.utctimetuple()) + float(dtime.microsecond)/1000000
    return time.mktime(dtime.timetuple()) + float(dtime.microsecond)/1000000

def from_timestamp(tstamp):
    if use_tz:
        return datetime.fromtimestamp(float(tstamp), tz=utc)
    return datetime.fromtimestamp(float(tstamp))
