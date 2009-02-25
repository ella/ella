from optparse import make_option
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from ella.newman.models import CategoryUserRole, DenormalizedCategoryUserRole

class Command(BaseCommand):
    help = 'Synchronizes CategoryUserRole objects to DenormalizedCategoryUserRole objects.'
    args = ""

    def handle(self, *fixture_labels, **options):
        verbosity = int(options.get('verbosity', 1))
        # start transaction
        transaction.commit_unless_managed()
        transaction.enter_transaction_management()
        transaction.managed(True)
        if verbosity > 1:
            print 'Transaction started'

        cur = connection.cursor()
        cur.execute('DELETE FROM %s' % DenormalizedCategoryUserRole._meta.db_table)
        for role in CategoryUserRole.objects.all():
            if verbosity > 0:
                print 'Saving denormalized %s' % role
            role.sync_denormalized()
        if verbosity > 0:
            print 'Denormalized object count: %d' % DenormalizedCategoryUserRole.objects.all().count()
        # commit changes to database
        transaction.commit()
        transaction.leave_transaction_management()
        if verbosity > 1:
            print 'Transaction committed'
