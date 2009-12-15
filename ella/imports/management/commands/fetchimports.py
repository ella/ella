import sys
import locale
import codecs

from django.db import transaction
from django.conf import settings
from django.utils import translation
from django.core.management.base import NoArgsCommand


# be able to redirect any non-ascii prints
sys.stdout = codecs.getwriter(locale.getdefaultlocale()[1])(sys.__stdout__)

@transaction.commit_on_success
def fetch(server):
    "Wrapped server.fetch() in transaction."
    server.fetch()

class Command(NoArgsCommand):
    help = 'Fetch all registered imports'

    def handle(self, *test_labels, **options):
        translation.activate(settings.LANGUAGE_CODE)

        errors = self.fetch_all()
        sys.exit(errors)

    def fetch_all(self):
        "Runs fetch on all Server. Return number of errors occured."
        from ella.imports.models import Server
        error_count = 0
        for server in Server.objects.all():
            try:
                fetch(server)
                print "OK %s " % (server.title,)
            except Exception, e:
                error_count += 1
                print "KO %s - %s" % (server.title, e)
        return error_count

