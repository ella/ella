from tempfile import gettempdir
from os.path import join

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS


DEBUG = False
TEMPLATE_DEBUG = DEBUG
DISABLE_CACHE_TEMPLATE = DEBUG


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
	'NAME': join(gettempdir(), 'ella_unit_project.db'),
	'TEST_NAME': join(gettempdir(), 'test_ella_unit_project.db'),
    }
}

TIME_ZONE = 'Europe/Prague'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# Make this unique, and don't share it with anybody.
SECRET_KEY = '88b-01f^x4lh$-s5-hdccnicekg07)niir2g6)93!0#k(=mfv$'

# TODO: Fix logging
# init logger
#LOGGING_CONFIG_FILE = join(dirname(testbed.__file__), 'settings', 'logger.ini')
#if isinstance(LOGGING_CONFIG_FILE, basestring) and isfile(LOGGING_CONFIG_FILE):
#    logging.config.fileConfig(LOGGING_CONFIG_FILE)

# we want to reset whole cache in test
# until we do that, don't use cache
CACHE_BACKEND = 'dummy://'

NEWMAN_MEDIA_PREFIX = '/static/newman_media/'

USE_PRIORITIES = True

TAG_LISTINGS_PAGINATE_BY = 1
