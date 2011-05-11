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

THUMB_DIMENSION_DEFAULT = (80,80)

FORMAT_QUALITY = FORMAT_QUALITY_DEFAULT
THUMB_DIMENSION = THUMB_DIMENSION_DEFAULT
DO_URL_CHECK = False
IMAGE_URL_PREFIX = ''
CUSTOM_SUBDIR = ''
UPLOAD_TO = CUSTOM_SUBDIR and 'photos/%s/%%Y/%%m/%%d' % CUSTOM_SUBDIR or 'photos/%Y/%m/%d'
EMPTY_IMAGE_SITE_PREFIX = ''

TYPE_EXTENSION = {
    'JPEG': '.jpg',
    'PNG': '.png',
    'GIF': '.gif'
}

PHOTO_MIN_WIDTH=150
PHOTO_MIN_HEIGHT=150

photos_settings = Settings('ella.photos.conf', 'PHOTOS')

