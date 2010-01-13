from os.path import dirname, join, normpath, pardir

FILE_ROOT = normpath(join(dirname(__file__), pardir))

USE_I18N = True

MEDIA_ROOT = join(FILE_ROOT, 'static')

MEDIA_URL = '/static/'

ADMIN_MEDIA_PREFIX = '/admin_media/'


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'unit_project.template_loader.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'ella.catlocks.middleware.CategoryLockMiddleware',
)

ROOT_URLCONF = 'unit_project.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    join(FILE_ROOT, 'templates'),

)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.media',
)

INSTALLED_APPS = (
    'ella.core',
    'ella.articles',
    'ella.photos',
    'ella.positions',
    'ella.newman',
    'ella.newman.licenses',
    'ella.galleries',
    'ella.catlocks',
    'ella.polls',
    'ella.interviews',
    'ella.ellaexports',
    'djangomarkup',
    'tagging',
    'threadedcomments',
    'ella.ellacomments',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.redirects',
    'django.contrib.admin',
    'django.contrib.comments',
)

COMMENTS_APP = 'ella.ellacomments'

DEFAULT_PAGE_ID = 1

VERSION = 1


