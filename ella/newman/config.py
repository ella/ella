"""
This module is intended to hold default constants.
Constants may be modified via project settings.py.
"""
from django.conf import settings

NEWMAN_URL_PREFIX = 'nm'

# AdminSettings
USER_CONFIG = 'newman_user_config'            # session key for AdminSettings JSON data
CATEGORY_FILTER = 'newman_category_filter'    # user defined category filtering on newman HP
NEWMAN_MARKUP_DEFAULT = getattr(settings, 'NEWMAN_MARKUP_DEFAULT', 'markdown')

# list of recipients for error reporting
ERR_REPORT_RECIPIENTS = getattr(settings, 'NEWMAN_ERR_REPORT_RECIPIENTS', ['ella.errors@gmail.com'])

# conversion functions mapping - from JSON to python (i.e. changing item datatypes etc.)
JSON_CONVERSIONS = (
    (CATEGORY_FILTER, 'decode_category_filter_json'),
)

# JsonResponse status "codes" (used instead of HTTP status codes)
STATUS_OK = "ok"
STATUS_GENERIC_ERROR = 'error'
STATUS_SMTP_ERROR = 'smtp_error'
STATUS_ADDED = 'added'
STATUS_MODIFIED = 'modified'
STATUS_FORM_ERROR = 'form_error'
STATUS_VAR_MISSING = 'variable_missing'
STATUS_OBJECT_NOT_FOUND = 'object_not_found'
STATUS_JSON_REDIRECT = 'redirect'
HTTP_OK = 200
HTTP_ERROR = 405

# Maximum autosave objects hold for bound object:
AUTOSAVE_MAX_AMOUNT = getattr(settings, 'NEWMAN_AUTOSAVE_MAX_AMOUNT', 3)

# List of applicable ContentTypes

NON_PUBLISHABLE_CTS = (
    'photos.photo',
    'polls.survey',
)

# Models that have TaggingInlineAdmin in inlines
TAGGED_MODELS = getattr(settings, 'TAGGED_MODELS', (
    'core.publishable',
    'articles.article',
    'galleries.gallery',
    'interviews.interview',
    'polls.quiz',
    # 'photos.photo',
))

NEWMAN_FAVORITE_ITEMS = getattr(settings, 'NEWMAN_FAVORITE_ITEMS', (
    'publishable',
    'article',
    'photo',
    'gallery',
    'survey',
    'quiz',
    'contest',
    'interview',
    'position',
))

# TODO try to load consts from django.conf.settings
