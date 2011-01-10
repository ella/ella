from optparse import make_option
from time import time, sleep

from django.core.management.base import BaseCommand
from django.db import connection, transaction, reset_queries
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
        print 'Sleeping for 20 sec before denormalization process will be started...'
        sleep(20)

def commit_work(run_transaction):
    if run_transaction:
        transaction.commit()
        transaction.leave_transaction_management()
        printv('Transaction committed')

def begin_work(run_transaction):
    if run_transaction:
        transaction.commit_unless_managed()
        transaction.enter_transaction_management()
        transaction.managed(True)
        printv('Transaction started')

def demoralize(run_transaction=True, verbosity=0):
    begin_work(run_transaction)
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
    commit_work(run_transaction)

def denormalize(username_list, run_transaction=True, verbosity=0):
    cur = connection.cursor()
    group_category = dict()
    denormalized = None
    prev_user = None

    queryset = CategoryUserRole.objects.select_related().order_by('user')
    if username_list:
        queryset = queryset.filter(user__username__in=username_list)

    for role in queryset.iterator():
        # Optimalization -- create dict for set of categories and certain group. Then copy this denorm. data and change only user field.
        key = u'%s_' % role.group
        for cat in role.category.order_by('-title').all():
            key += u'%s-' % cat.title

        # Transaction handling, deleting all rows with actual role.user_id
        if prev_user != role.user:
            # ommit commit when processing first user
            if prev_user is not None:
                commit_work(run_transaction)
            reset_queries()
            begin_work(run_transaction)
            begin = time()
            cur.execute(
                'DELETE FROM %s WHERE user_id = %d;' %
                (DenormalizedCategoryUserRole._meta.db_table, role.user.pk)
            )
            printv('Delete took %f sec.' % (time() - begin))

        if key in group_category:
            printv('Saving denormalized %s (fast)' % role, STD_VERB)
            user_id = role.user.pk
            begin = time()
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
            printv('Took %f sec' % (time() - begin))
        else:
            printv('Saving denormalized %s' % role, STD_VERB)
            begin = time()
            denormalized = role.sync_denormalized()
            printv('Took %f sec' % (time() - begin))
            group_category[key] = denormalized

        prev_user = role.user

    commit_work(run_transaction)
    printv('Denormalized object count: %d' % DenormalizedCategoryUserRole.objects.all().count(), STD_VERB)

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--notransaction', action='store_true', dest='start_transaction',
            help='If specified synchronization won\'t be performed inside transaction.'),
    )
    help = 'Synchronizes CategoryUserRole objects to DenormalizedCategoryUserRole objects.'
    args = "[username ...]"

    def handle(self, *username_list, **options):
        global verbosity
        check_settings()
        verbosity = int(options.get('verbosity', 1))
        run_transaction = not options.get('start_transaction', False)
        printv('Run in transaction: %s' % run_transaction)

        denormalize(username_list, run_transaction, verbosity)
