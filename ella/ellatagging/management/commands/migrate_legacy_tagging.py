from optparse import make_option

from _mysql_exceptions import OperationalError

from django.core.management.base import CommandError, BaseCommand

from south.db import db
from south.models import MigrationHistory

class Command(BaseCommand):

    help = 'Migrates db structure from abandonded ella.tagging app to ella.ellatagging'

    def handle(self, *args, **options):

        confirm = raw_input('\n'.join((
            'This will alter a db table tagging_taggeditem dropping category_id and priority columns',
            'Are you sure you want to do this?',
            '',
            "Type 'yes' to continue, or 'no' to cancel: ")))
        
        if confirm != 'yes':
            print "Migration cancelled."
            return

        try:
            db.delete_column('tagging_taggeditem', 'category_id')
            print "Column category_id deleted."
            db.delete_column('tagging_taggeditem', 'priority')
            print "Column priority deleted."
        except OperationalError:
            print "Can't drop columns (already gone?)"

        MigrationHistory.objects.filter(app_name='tagging').delete()
        print 'Tagging migrations deleted from South migration hystory.'

