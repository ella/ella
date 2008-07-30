import sys, locale, codecs
from datetime import datetime

from django.core.management.base import NoArgsCommand

from ella.reminders.library import library

# be able to redirect any non-ascii prints
sys.stdout = codecs.getwriter(locale.getdefaultlocale()[1])(sys.__stdout__)


class Command(NoArgsCommand):
    help = 'Send all reminders'

    def handle(self, *test_labels, **options):
        now = datetime.now() # TODO - allow overriding the time from commandline
        library.send_all(now)



