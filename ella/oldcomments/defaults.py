"""
shared mini settings for ella.comments application (forms, models)
"""

from django.conf import settings
from django.utils.translation import gettext_lazy as _


NICKNAME_LENGTH = 50
USERNAME_LENGTH = 50
OPTS_LENGTH = 100
TARGET_LENGTH = 50
SUBJECT_LENGTH = 100
COMMENT_LENGTH = 3000

OPTS_DELIM = ':'
FORM_OPTIONS = {
    'LOGGED_ONLY': 'LO',
    'UNAUTHORIZED_ONLY': 'UN',
}

PATH_LENGTH=500
PATH_SEPARATOR='/'

USER_CHOICE=(
        ('RE', _('registered user')),
        ('AN', _('anonymous user')),
)

FORM_TIMEOUT = 3600
POST_TIMEOUT = 3600
INIT_PROPS = {
    'options': '',
    'target': '',
    'gonzo': '',
    'parent': None,
}

FORM_TIMEOUT = getattr(settings, 'COMMENTS_FORM_TIMEOUT', FORM_TIMEOUT)
POST_TIMEOUT = getattr(settings, 'COMMENTS_POST_TIMEOUT', POST_TIMEOUT)
INIT_PROPS   = getattr(settings, 'COMMENTS_INIT_PROPS', INIT_PROPS)

