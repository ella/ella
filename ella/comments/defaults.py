# mini settings for ella.comments application
# TODO: at the end check for default values from global settings

from django.conf import settings
from django.utils.translation import gettext_lazy as _

NICKNAME_LENGTH = 50
USERNAME_LENGTH = 50
OPTS_LENGTH = 100
TARGET_LENGTH = 50
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

FORM_TIMEOUT = 3600
INIT_PROPS = {
    OPTIONS_NAME: '',
    TARGET_NAME: '',
    HASH_NAME: '',
    PARENT_NAME: None,
}

PATH_LENGTH=500
PATH_SEPARATOR='/'

USER_CHOICE=(
        ('RE', _('registered user')),
        ('AN', _('anonymous user')),
)

POST_TIMEOUT = 3600

