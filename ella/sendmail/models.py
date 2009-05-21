from django.db import models
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _

class Mail(models.Model):
    sender = models.EmailField()
    recipient = models.EmailField()
    sent = models.DateTimeField(default=datetime.now)
    target_ct = models.ForeignKey(ContentType, verbose_name=_('content type'))
    target_id    = models.PositiveIntegerField(_('target id'), db_index=True)
    content = models.TextField(blank=True, null=True)

