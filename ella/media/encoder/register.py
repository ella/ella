# register admin options
import ella.media.encoder.admin

# queue register
from ella.media.encoder.models import FormattedFile
from ella.media.queue import QUEUE as ELLA_QUEUE
ELLA_QUEUE.register('ella/media/encoder/formattedfile', FormattedFile.objects.create_in_format)

