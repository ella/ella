from os.path import dirname, join, normpath, pardir

FILE_ROOT = normpath(join(dirname(__file__), pardir))

USE_I18N = True

USE_TZ = True

MEDIA_ROOT = join(FILE_ROOT, 'static')

STATIC_URL = MEDIA_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'test_ella.template_loader.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'test_ella.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    join(FILE_ROOT, 'templates'),

)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.media',
    'django.contrib.auth.context_processors.auth',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.redirects',
    'django.contrib.admin',

    'ella.api',
    'ella.core',
    'ella.articles',
    'ella.photos',
    'ella.positions',
    'test_ella.test_app',
)

LISTING_HANDLERS = {
    'default': 'ella.core.managers.ModelListingHandler',
    'redis': 'ella.core.cache.redis.TimeBasedListingHandler',
}
LISTINGS_REDIS = {}
USE_REDIS_FOR_LISTINGS = True
REDIS_LISTING_HANDLER = 'redis'

DEFAULT_PAGE_ID = 1

VERSION = 1


CATEGORY_TEMPLATES = [
    ('category.html', ''),
    ('static_page.html', ''),
]

PHOTOS_DEFAULT_BG_COLOR = 'blue'

API_ENABLED = True
