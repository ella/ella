import commands # this means, we are unix specific
from datetime import datetime
from os import path
import sha
import re

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from ella.utils.filemanipulation import file_rename
from ella.media.queue import QUEUE as ELLA_QUEUE


ACTIVE_MQ_HOST = getattr(settings, 'ACTIVE_MQ_HOST', None)
UPLOAD_ROOT = settings.UPLOAD_ROOT
UPLOAD_URL  = settings.UPLOAD_URL
RE_SPACEEND = re.compile(r'\s*;?\s*$', re.MULTILINE)


class Format(models.Model):
    name = models.CharField(_('Format name'), max_length=80, unique=True,
            help_text=_('this should be in some sluggy format'))
    from_type = models.CharField(_('From what type'), max_length=100)
    to_type = models.CharField(_('To what type'), max_length=100)
    conversion_script = models.TextField(_('Conversion script'),
            help_text=_('\n'.join([
                'this will be interpretted as string with given variables:',
                ' * source_hash',
                ' * formatted_file_name',
                ' * source_file_type',
                ' * formatted_file_type',
                ' * format_name',
                ' * upload_root',
                ]))
)

    def run(self, kwargs):
        """
        get string from database
        substitute its variables and
        run as shell command
        """
        command = self.conversion_script % kwargs
        status, output = commands.getstatusoutput(command)

        log = 'COMMAND:\n%s\nOUTPUT:\n%s\nSTATUS:\n%s\n\n' % (command, output, status)
        print log

        return status

    def save(self):
        # TODO: saved format invoke registering message
        self.conversion_script = self.conversion_script.replace('\r\n', '\n')
        self.conversion_script = RE_SPACEEND.sub('', self.conversion_script)
        super(Format, self).save()

    def __unicode__(self):
        return self.name

class FormattedFileManager(models.Manager):
    def create_in_format(self, data):
        """
        create formatted file in specified format
        this method should get all data
        that will be postponed to Format.conversion_script
        """
        format = Format.objects.get(name=data['format_name'])
        file = path.join(UPLOAD_ROOT, data['formatted_file_name'])

        data['upload_root'] = UPLOAD_ROOT
        status = format.run(data)

        formattedfile = self.create(source_hash=data['source_hash'], format=format, file=file, status=status)

class FormattedFile(models.Model):
    source_hash = models.CharField(_('Source file hash'), max_length=40, blank=True)
    format = models.ForeignKey(Format, verbose_name=_('Format'))
    hash = models.CharField(_('Content hash'), max_length=40, blank=True)
    file = models.FileField(_('Formatted file'), upload_to=UPLOAD_ROOT,
            help_text=_('here you can upload your own formatted file'))
    metadata = models.TextField(_('Meta data'), blank=True,
            help_text=_('meta data xml - should be generated after file save'))
    status = models.IntegerField(_('Exit status'), blank=True, null=True)

    objects = FormattedFileManager()

    @property
    def type(self):
        return self.format.to_type

    def send_signal(self):
        """tell others that formatted file has been generated"""
        formattedfile = dict(
                    source = self.source_hash,
                    format = self.format.name,
                    hash = self.hash,
                    url = UPLOAD_URL + self.file.lstrip(UPLOAD_ROOT),
                    metadata = '', #TODO
                    status = self.status,
)
        ELLA_QUEUE.put('ella/media/formattedfile', formattedfile)

    def save(self):
        f = open(self.file, 'r')
        self.hash = sha.new(f.read()).hexdigest()
        f.close()
        self.file = file_rename(self.file, self.hash, '')

        super(FormattedFile, self).save()

        # send signal about successful file save
        self.send_signal()

    class Meta:
        unique_together = (('source_hash', 'format'),)

    def __unicode__(self):
        return "%s-%s" % (self.source_hash, self.format.name)

