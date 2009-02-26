from optparse import make_option
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from ella.newman.models import CategoryUserRole, DenormalizedCategoryUserRole

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--notransaction', action='store_true', dest='start_transaction',
            help='If specified synchronization won\'t be performed inside transaction.'),
    )
    help = 'Synchronizes CategoryUserRole objects to DenormalizedCategoryUserRole objects.'
    args = ""

    def handle(self, *fixture_labels, **options):
        verbosity = int(options.get('verbosity', 1))
        verbosity = int(options.get('verbosity', 1))
        run_transaction = not options.get('start_transaction', False)
        # start transaction
        if run_transaction:
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
        if run_transaction:
            transaction.commit()
            transaction.leave_transaction_management()
            if verbosity > 1:
                print 'Transaction committed'
