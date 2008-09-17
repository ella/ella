from datetime import datetime
import sha

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from ella.utils.filemanipulation import file_rename
from ella.media.queue import QUEUE as ELLA_QUEUE


ACTIVE_MQ_HOST = getattr(settings, 'ACTIVE_MQ_HOST', None)
UPLOAD_ROOT = settings.UPLOAD_ROOT
UPLOAD_URL  = settings.UPLOAD_URL


class Upload(models.Model):
    """dummy model for direct source files uploading from admin"""

    title = models.CharField(_('Title'), max_length=255)
    hash = models.CharField(_('Content hash'), max_length=40, blank=True)
    file = models.FileField(_('Source file'), upload_to=UPLOAD_ROOT)
    type = models.CharField(_('Type of this file'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    uploaded = models.DateTimeField(default=datetime.now, editable=False)

    def send_signal(self):
        """tell others that some file has been uploaded"""
        source = dict(
                    title = self.title,
                    hash = self.hash,
                    url = UPLOAD_URL + self.file.lstrip(UPLOAD_ROOT),
                    type = self.type,
                    metadata = '', #TODO
                    description = self.description,
                    uploaded = self.uploaded,
)
        ELLA_QUEUE.put('ella/media/source', source)

    def save(self, force_insert=False, force_update=False):
        f = open(self.file, 'r')
        self.hash = sha.new(f.read()).hexdigest()
        f.close()
        self.file = file_rename(self.file, self.hash, '')

        super(Upload, self).save(force_insert, force_update)

        # send signal about successful file save
        self.send_signal()

    def __unicode__(self):
        return self.hash

