from django.utils.translation import ugettext_lazy as _
from ella.utils.settings import Settings

# settings default
FORMAT_QUALITY_DEFAULT = (
    (45, _('Low')),
    (65, _('Medium')),
    (75, _('Good')),
    (85, _('Better')),
    (95, _('High')),
)


FORMAT_QUALITY = FORMAT_QUALITY_DEFAULT
CUSTOM_SUBDIR = ''
UPLOAD_TO = CUSTOM_SUBDIR and 'photos/%s/%%Y/%%m/%%d' % CUSTOM_SUBDIR or 'photos/%Y/%m/%d'
EMPTY_IMAGE_SITE_PREFIX = ''

TYPE_EXTENSION = {
    'JPEG': '.jpg',
    'PNG': '.png',
    'GIF': '.gif'
}

PHOTO_MIN_WIDTH = 150
PHOTO_MIN_HEIGHT = 150

DEFAULT_BG_COLOR = 'black'

FORMATED_PHOTO_FILENAME = None

DEBUG = False
DEBUG_PLACEHOLDER_PROVIDER_TEMPLATE = 'http://placehold.it/%(width)sx%(height)s'

photos_settings = Settings('ella.photos.conf', 'PHOTOS')

