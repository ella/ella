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

# Newman base URL (suitable when newman_frontend_tags' tags is used)
BASE_URL = getattr(settings, 'NEWMAN_BASE_URL', '')

# Maximum autosave objects hold for bound object:
AUTOSAVE_MAX_AMOUNT = getattr(settings, 'NEWMAN_AUTOSAVE_MAX_AMOUNT', 3)

# List of applicable ContentTypes
NON_PUBLISHABLE_CTS = getattr(settings, 'NEWMAN_NON_PUBLISHABLE_CTS', (
    'photos.photo',
    'polls.poll',
    'polls.survey',
))

# Models that have TaggingInlineAdmin in inlines
TAGGED_MODELS = getattr(settings, 'NEWMAN_TAGGED_MODELS', (
    'core.publishable',
    'articles.article',
    'galleries.gallery',
    'interviews.interview',
    'polls.quiz',
    'polls.contest',
))

# Exportable publishables
EXPORTABLE_MODELS = getattr(settings, 'NEWMAN_EXPORTABLE_MODELS', (
    'core.publishable',
    'articles.article',
    'galleries.gallery',
    'interviews.interview',
    'polls.quiz',
    'polls.contest',
))

NEWMAN_FAVORITE_ITEMS = getattr(settings, 'NEWMAN_FAVORITE_ITEMS', (
    'core.publishable',
    'articles.article',
    'photos.photo',
    'galleries.gallery',
    'polls.survey',
    'polls.quiz',
    'polls.contest',
    'interviews.interview',
    'positions.position',
))

EDITOR_PREVIEW_CSS = getattr(settings, 'NEWMAN_EDITOR_PREVIEW_CSS', None)
EDITOR_PREVIEW_TEMPLATE = getattr(settings, 'NEWMAN_EDITOR_PREVIEW_TEMPLATE', None)

# TODO try to load consts from django.conf.settings
