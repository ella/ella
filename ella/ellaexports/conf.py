from datetime import timedelta
from ella.utils.settings import Settings

POSITION_IS_NOT_OVERLOADED = 0
DATETIME_FORMAT = '%Y-%m-%d %H:%M'
TIME_FORMAT = '%H:%M'
FEED_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S+02:00' #TODO settings.py

# timeline
TIMELINE_STEP = timedelta(hours=2)  # two hours by default
EMPTY_TIMELINE_CELL = None
DAY_MAX_HOUR = 23
RANGE_DAYS = 14
RANGE_WIDTH_HOURS = 2


ellaexports_settings = Settings('ella.ellaexports.conf', 'EXPORTS')
