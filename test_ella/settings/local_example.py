"""
Rename to local.py and set variables from config.py that
You want to override.
"""
from test_ella.settings.base import TEMPLATE_LOADERS

TEMPLATE_LOADERS = list(TEMPLATE_LOADERS) + ['django.template.loaders.app_directories.Loader',]

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DISABLE_CACHE_TEMPLATE = DEBUG

ROOT_URLCONF = 'test_ella.working_urls'
