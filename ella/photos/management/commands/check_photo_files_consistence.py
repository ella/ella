import re
import os
import sys
from optparse import make_option
from django.core.management.base import CommandError, BaseCommand
from ella.photos.conf import photos_settings
from pprint import pprint


class Command(BaseCommand):

    help = 'Check consistence between database records and coresponding image files'

    VERBOSITY_ERROR = 0
    VERBOSITY_WARNING = 1
    VERBOSITY_STAT = 1
    VERBOSITY_INFO = 2
    VERBOSITY_DEBUG = 3

    verbosity = VERBOSITY_STAT
    delete = False
    all = False
    extensions = None
    extensions_ic = True

    option_list = BaseCommand.option_list + (
        make_option('--delete',
            action='store_true',
            dest='delete',
            default=delete,
            help='Delete unlinked image files'),
        make_option('--all',
            action='store_true',
            dest='all',
            default=all,
            help='Delete all unlinked files'),
        make_option('--extensions',
            dest='extensions',
            default=extensions,
            help='Specify comma separated extensions (with ".") of photos'),
        make_option('--extensions-no-ignore-case',
            dest='extensions_ic',
            default=extensions_ic,
            help='Case sensitive comparation of extensions'),
        )

    def process_options(self, options):
        self.verbosity = int(options['verbosity'])
        self.delete = bool(options['delete'])
        self.all = bool(options['all'])
        self.extensions = options['extensions'] and options['extensions'].split(',')
        self.extensions_ic = options['extensions_ic']

    def print_message(self, message, level, fd=None):
        if level <= self.verbosity:
            if fd:
                try:
                    print >> fd, message
                except IOError:
                    pass
            else:
                print message

    def print_error(self, message):
        self.print_message(message, self.VERBOSITY_ERROR, sys.stderr)

    def print_warning(self, message):
        self.print_message(message, self.VERBOSITY_WARNING)

    def print_stat(self, message):
        self.print_message(message, self.VERBOSITY_STAT)

    def print_info(self, message):
        self.print_message(message, self.VERBOSITY_INFO)

    def print_debug(self, message):
        self.print_message(message, self.VERBOSITY_DEBUG)

    def handle(self, *args, **options):

        self.process_options(options)
        self.print_debug("Options: ")
        self.print_debug(options)

        subdir = re.sub(
            '[^('+re.escape(os.sep)+')]*%[^%].*',
            '',
            photos_settings.UPLOAD_TO
            ).strip(os.sep)

        from ella.photos.models import Photo
        storage = Photo().image.storage

        extensions = self.extensions or photos_settings.TYPE_EXTENSION.values()
        self.print_info('Accepted extensions: ' +str(extensions))
        photo_extension_re = re.compile(
                '(%s)$' % ('|'.join([re.escape(ex) for ex in extensions])),
                self.extensions_ic and re.IGNORECASE or 0)

        # breadth-first search
        files = []
        nodes = [subdir]
        while nodes:
            current = nodes.pop()
            self.print_debug("Entering directory '%s'" % current)
            current_dirs, current_files = storage.listdir(current)

            if not (current_dirs or current_files):
                self.print_info("Directory '%s' is empty" % current)
            else:
                nodes += [
                        '%s%s%s' % (current, os.sep, directory)
                        for directory in current_dirs]

                for current_file in current_files:
                    f = '%s%s%s' % (current, os.sep, current_file)
                    is_image = bool(photo_extension_re.search(current_file))
                    if not is_image:
                        self.print_info("File '%s' is not image" % f)
                    if is_image or self.all:
                        files.append(f)
                        self.print_debug("Appending file '%s'" % f)

            self.print_debug("Leaving directory '%s'" % current)

        photo_files_set = set(files)
        db_files_set = set([photo.image.url for photo in Photo.objects.all()])
        self.print_summarization(photo_files_set, db_files_set)

        if self.delete:
            self.delete_files(storage, photo_files_set -db_files_set)

    def print_summarization(self, photo_files_set, db_files_set):

        self.print_stat("Count of files on disk (selected extensions): %d"
                % len(photo_files_set))

        self.print_stat("Count of files in database (all extensions): %d"
                % len(db_files_set))

        only_in_database = db_files_set -photo_files_set
        self.print_info("Files only in database (all extensions):")
        self.print_info(only_in_database)
        self.print_stat("Count of files only in database (all extensions): %d"
                % len(only_in_database))

        only_on_disk = photo_files_set -db_files_set
        self.print_info("Files only on disk (selected extensions):")
        self.print_info(only_on_disk)
        self.print_stat("Count of files only on disk (selected extensions): %d"
                % len(only_on_disk))

        self.print_stat("Count of paired files (selected extensions): %d"
                % len(photo_files_set & db_files_set))


    def delete_files(self, storage, to_delete):
            for f in to_delete:
                self.print_info("Delete file '%s'" % f)
                storage.delete(f)
            self.print_stat("%d files are deleted" % len(to_delete))

