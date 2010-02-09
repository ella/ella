from optparse import make_option
import sys

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from ella.newman.models import CategoryUserRole, DenormalizedCategoryUserRole

NO_VERB = 0
STD_VERB = 1
HIGH_VERB = 2
verbosity = None

def printv(text, verb=HIGH_VERB):
    if verb <= verbosity:
        print text

def check_settings():
    from django.conf import settings
    if settings.DEBUG:
        print 'settings.DEBUG was set to True. This causes huge performance penalty. Aborting.'
        sys.exit(1)

def demoralize(run_transaction=True, verbosity=0):
    if run_transaction:
        transaction.commit_unless_managed()
        transaction.enter_transaction_management()
        transaction.managed(True)
        printv('Transaction started')

    cur = connection.cursor()
    cur.execute('DELETE FROM %s' % DenormalizedCategoryUserRole._meta.db_table)
    group_category = dict()
    denormalized = None
    '''5181183-core.delete_placement-223-1-63'''
    for role in CategoryUserRole.objects.all():
        # Optimalization -- create dict for set of categories and certain group. Then copy this denorm. data and change only user field.
        key = u'%s_' % role.group
        for cat in role.category.all():
            key += u'%s-' % cat.title
        if key in group_category:
            printv('Saving denormalized %s (fast)' % role, STD_VERB)
            user_id = role.user.pk
            for d in group_category[key]:
                #copy denorm. data
                nd = DenormalizedCategoryUserRole(
                    contenttype_id=d.contenttype_id,
                    user_id=user_id,
                    permission_codename=d.permission_codename,
                    permission_id=d.permission_id,
                    category_id=d.category_id,
                    root_category_id=d.root_category_id
                )
                try:
                    nd.save()
                except Exception, e:
                    printv(str(e))
        else:
            printv('Saving denormalized %s' % role, STD_VERB)
            denormalized = role.sync_denormalized()
            group_category[key] = denormalized

    printv('Denormalized object count: %d' % DenormalizedCategoryUserRole.objects.all().count(), STD_VERB)
    # commit changes to database
    if run_transaction:
        transaction.commit()
        transaction.leave_transaction_management()
        printv('Transaction committed')


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--notransaction', action='store_true', dest='start_transaction',
            help='If specified synchronization won\'t be performed inside transaction.'),
    )
    help = 'Synchronizes CategoryUserRole objects to DenormalizedCategoryUserRole objects.'
    args = ""

    def handle(self, *fixture_labels, **options):
        global verbosity
        verbosity = int(options.get('verbosity', 1))
        run_transaction = not options.get('start_transaction', False)
        printv('Run in transaction: %s' % run_transaction)

        denormalize(run_transaction, verbosity)
