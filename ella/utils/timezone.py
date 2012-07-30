import time
import calendar
from pytz import utc
from datetime import datetime

from django.conf import settings

use_tz = getattr(settings, 'USE_TZ', False)
try:
    # try import offset-aware datetime from Django >= 1.4
    from django.utils.timezone import now
except ImportError:
    # backward compatibility with Django < 1.4 (offset-naive datetimes)
    from datetime import datetime
    now = datetime.now
    use_tz = False


def localize(dtime):
    if use_tz:
        return utc.localize(dtime)
    return dtime

def to_timestamp(dtime):
    if use_tz:
        return calendar.timegm(dtime.utctimetuple()) + float(dtime.microsecond)/1000000
    return time.mktime(dtime.timetuple())

def from_timestamp(tstamp):
    if use_tz:
        return datetime.fromtimestamp(tstamp, tz=utc)
    return datetime.fromtimestamp(tstamp)
