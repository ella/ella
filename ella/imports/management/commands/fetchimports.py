import sys
import locale
import codecs

from django.core.management.base import NoArgsCommand


# be able to redirect any non-ascii prints
sys.stdout = codecs.getwriter(locale.getdefaultlocale()[1])(sys.__stdout__)


class Command(NoArgsCommand):
    help = 'Fetch all registered imports'

    def handle(self, *test_labels, **options):
        errors = self.fetch_all()
        sys.exit(errors)

    def fetch_all(self):
        from ella.imports.models import Server
        error_count = 0
        for server in Server.objects.all():
            try:
                server.fetch()
                print "OK %s " % (server.title,)
            except Exception, e:
                error_count += 1
                print "KO %s - %s" % (server.title, e)
        return error_count

