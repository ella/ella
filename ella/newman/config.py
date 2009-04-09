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

# conversion functions mapping - from JSON to python (i.e. changing item datatypes etc.)
JSON_CONVERSIONS = (
    (CATEGORY_FILTER, 'decode_category_filter_json'),
)

# JsonResponse status "codes" (used instead of HTTP status codes)
STATUS_OK = "ok"
STATUS_GENERIC_ERROR = "error"
STATUS_SMTP_ERROR = "smtp_error"
STATUS_ADDED = "added" 
STATUS_MODIFIED = "modified" 
STATUS_FORM_ERROR = "form_error" 
STATUS_VAR_MISSING = "variable_missing" 
STATUS_OBJECT_NOT_FOUND = "object_not_found" 


# TODO try to load consts from django.conf.settings
