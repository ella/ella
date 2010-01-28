from optparse import make_option

from _mysql_exceptions import OperationalError

from django.core.management.base import CommandError, BaseCommand

from south.db import db

class Command(BaseCommand):

    help = 'Migrates db structure from abandonded ella.tagging app to ella.ellatagging'

    def handle(self, *args, **options):

        try:
            db.delete_column('tagging_taggeditem', 'category_id')
            print "Column category_id deleted."
            db.delete_column('tagging_taggeditem', 'priority')
            print "Column priority deleted."
        except OperationalError:
            print "Can't drop columns (already gone?)"

