from datetime import datetime
import commands # this means, we are unix specific
from os import path

from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_str
from django.db import models, transaction
from django.conf import settings

from ella.utils.filemanipulation import file_rename
from ella.db import fields


class Type(models.Model):
    name = models.CharField(_('Type name'), max_length=80)
    extension = models.CharField(_('File extension'), max_length=10, blank=True,
            help_text=_('formatted file extension of this type will be changed to this value if given'))
    metadata_schema = models.TextField(_('Meta data schema'), blank=True,
            help_text=_('every media file validates its xml meta data to this schema'))

    def __unicode__(self):
        return self.name

class Source(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    slug = models.CharField(_('Slug'), db_index=True, max_length=255)
    file = models.FileField(_('Source file'), upload_to='media/source/%Y/%m/%d')
    type = models.ForeignKey(Type, verbose_name=_('Type of this file'))
    metadata = fields.XMLMetaDataField(_('Meta data'), blank=True, schema_path='type.metadata_schema', schema_type=None,
            help_text=_('meta data xml - should be generated after file save'))

    description = models.TextField(_('Description'), blank=True)
    uploaded = models.DateTimeField(default=datetime.now, editable=False)

    @transaction.commit_on_success
    def save(self):
        if not self.id:
            # prefill the slug with the ID, it requires double save
            super(Source, self).save()
            self.slug = '%s-%s' % (self.id, self.slug)
        # rename file by slug
        self.file = file_rename(self.file, self.slug)
        super(Source, self).save()

    def __unicode__(self):
        return self.title

class Format(models.Model):
    name = models.CharField(_('Format name'), max_length=80,
            help_text=_('this should be in some sluggy format'))
    from_type = models.ForeignKey(Type, related_name='format_from_set',
            verbose_name=_('From what type'))
    to_type = models.ForeignKey(Type, related_name='format_to_set',
            verbose_name=_('To what type'))
    conversion_script = models.TextField(_('Conversion script'),
            help_text=_('\n'.join([
                'this will be interpretted as string with given variables:',
                ' * source_file_name',
                ' * formatted_file_name',
                ' * source_file_type',
                ' * formatted_file_type',
                ' * format_name',
                ' * format_id',
                ])))

    def __unicode__(self):
        return self.name

class FormattedFile(models.Model):
    source = models.ForeignKey(Source, verbose_name=_('Source file'))
    format = models.ForeignKey(Format, verbose_name=_('Format'))
    file = models.FileField(_('Formatted file'), upload_to='media/formatted/%Y/%m/%d', blank=True,
            help_text=_('upload this file only if you do not want it created automaticly'))
    metadata = models.TextField(_('Meta data'), blank=True,
            help_text=_('meta data xml - should be generated after file save'))
#    metadata = xmlfields.XMLMetaDataField(_('Meta data'), blank=True, schema_path='type.metadata_schema', schema_type=None,
#            help_text=_('meta data xml - should be generated after file save'))
    exit_status = models.IntegerField(_('Exit status'), blank=True, null=True)

    @property
    def type(self):
        return self.format.to_type

    @transaction.commit_on_success
    def save(self):
        filename = '%s-%s' % (self.format_id, self.source.slug)
        extension = self.format.to_type.extension

        if self.file:
            # formatted file is uploaded directly, only rename
            self.file = file_rename(self.file, filename, extension)
        else:
            # get new filename
            if not extension:
                extension = path.splitext(self.source.file)[1]
            dir_path = datetime.now().strftime(smart_str(self._meta.get_field('file').upload_to))
            self.filename = file_rename('%s/' % dir_path, filename, extension, False)

            # formatted file is generated in here
            status = self.run_command()

            if status:
                # exit status of executed commands was different than zero
                # which means failure
                # TODO: log
                pass
            else:
                # othervise we expect,
                # that script creates given file successfully
                # and we can create reference into db
                self.file = self.filename

            # save exit status of command in generated files
            self.exit_status = status

        super(FormattedFile, self).save()

    def run_command(self):
        '''
        get string from database
        substitute its variables and
        run as shell command
        '''
        command_params = {
                'source_file_name' : path.join(settings.MEDIA_ROOT, self.source.file),
                'formatted_file_name' : path.join(settings.MEDIA_ROOT, self.filename),
                'source_file_type' : '',
                'formatted_file_type' : '',
                'format_name' : '',
                'format_id' : '',
}
        command = self.format.conversion_script.replace('\r\n', '\n') % command_params
        status, output = commands.getstatusoutput(command)

        log = 'COMMAND:\n%s\nOUTPUT:\n%s\nSTATUS:\n%s\n\n' % (command, output, status)
        print log

        return status

    class Meta:
        unique_together = (('source', 'format'),)

    def __unicode__(self):
        return "%s['%s']" % (self.source, self.format)


# initialization
from ella.media import register
del register

