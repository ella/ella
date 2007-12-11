'''mini settings for ella.comments application'''

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.conf import settings

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

OPTIONS_NAME = 'options'
TARGET_NAME = 'target'
HASH_NAME = 'gonzo'
PARENT_NAME = 'parent'

PATH_LENGTH=500
PATH_SEPARATOR='/'

USER_CHOICE=(
        ('RE', _('registered user')),
        ('AN', _('anonymous user')),
)

FORM_TIMEOUT = 3600
POST_TIMEOUT = 3600
INIT_PROPS = {
    OPTIONS_NAME: '',
    TARGET_NAME: '',
    HASH_NAME: '',
    PARENT_NAME: None,
}

FORM_TIMEOUT = getattr(settings, 'COMMENTS_FORM_TIMEOUT', FORM_TIMEOUT)
POST_TIMEOUT = getattr(settings, 'COMMENTS_POST_TIMEOUT', POST_TIMEOUT)
INIT_PROPS   = getattr(settings, 'COMMENTS_INIT_PROPS', INIT_PROPS)

