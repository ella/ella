import logging.config
from os.path import dirname, join, isfile

import testbed


DEBUG = True
TEMPLATE_DEBUG = DEBUG
DISABLE_CACHE_TEMPLATE = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = '/tmp/newman.db'  # Or path to database file if using sqlite3.
#TEST_DATABASE_NAME = '/tmp/mypage.db' # we need physical file due to use of threads in fetch_widgets
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Prague'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = join(dirname(testbed.__file__), 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/testbed'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '88b-01f^x4lh$-s5-hdccnicekg07)niir2g6)93!0#k(=mfv$'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'testbed.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    join(dirname(testbed.__file__), 'templates'),

)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.media',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',

    'testbed.service',
    'ella.core',
    'ella.articles',
    'ella.newman',
    'ella.newman.markup',
    'ella.core',
    'ella.articles',
    'ella.comments',
    'ella.photos',
    'ella.db_templates',
    'ella.galleries',
    'ella.polls',
    'ella.tagging',
    'ella.ratings',
    'ella.attachments',
    'ella.answers',
    'ella.series',
    'ella.imports',
    'ella.ellaadmin',
    'ella.discussions',
    'ella.interviews',
    'ella.positions',
    'ella.catlocks',
    'ella.sendmail',

    'recepty.recipes',
    'recepty.newsletters',

    'horoskopy.astrology',

    # Video
    'nc.cdnclient',
    'ella.media',
    'ella.contact_form',
    'jaknato.instruction',

)

# different urls than in normal frontend
ROOT_URLCONF = 'admin.newman.urls'

# Used for encoding and serving videos
CDN_API_SERVER_NAME = 'cnt-cdn-db.dev.chservices.cz:8301'

DEFAULT_PAGE_ID = 1

# cache widget's data for one hour
WIDGET_DATA_TIMEOUT = 60*60

# fetch widgets in one thread only to avoid locking issues with sqlite
FETCHWIDGET_THREADS = 1

# init logger
LOGGING_CONFIG_FILE = join(dirname(testbed.__file__), 'settings', 'logger.ini')
if isinstance(LOGGING_CONFIG_FILE, basestring) and isfile(LOGGING_CONFIG_FILE):
    logging.config.fileConfig(LOGGING_CONFIG_FILE)

PAGE_TEMPLATES = (
    ('page1.html', 'Page 1', 1),
    ('page2.html', 'Page 2', 2),
    ('page.html', 'Default', 5),
)

VERSION = 1

# we want to reset whole cache in test
CACHE_BACKEND = 'locmem://'

try:
    from testbed.settings.local import *
except ImportError:
    pass

