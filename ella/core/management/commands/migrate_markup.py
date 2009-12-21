import re
import sys

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import NoArgsCommand
from django.conf import settings
from django.db.transaction import is_dirty, commit, rollback, \
    enter_transaction_management, leave_transaction_management, managed
from django.db.models import get_model

from djangomarkup.models import SourceText, TextProcessor


lookup = None
def create_id_lookup():
    from ella.core.models import Publishable
    global lookup
    if lookup is None:
        lookup = dict(
            ((p['content_type'], p['old_id']), p['id'])
                for p in Publishable.objects.order_by().extra(select={'old_id': 'old_id'}).values('id', 'old_id', 'content_type') 
        )

BOX_RE = re.compile(r'''
        {% \s* box \s*      # {%_box_
        ([\w_]+)            # NAME 
        \s+ for \s+         # _for_
        (\w+)\.(\w+)        # APP.MODEL
        \s+ with \s+ pk \s+ # _with_pk_
        (\d+)               # PK
        \s*%}               # _%}
    ''', re.VERBOSE)

def update_field(instance, content_type):
    from ella.core.models import Dependency
    def update_one_box(match):
        name, app, model, pk = match.groups()

        # get content types
        ct = ContentType.objects.get_for_model(get_model(app, model))

        # update the pk value
        new_pk = lookup.get((ct.pk, int(pk)), pk)

        # report this box use as a dependency
        Dependency.objects.create(
                dependent_ct=content_type,
                dependent_id=instance.pk,

                target_ct=ct,
                target_id=new_pk
            )
        if new_pk != pk:
            sys.stdout.write('#')
        else:
            sys.stdout.write('-')

        # put everything together
        return '{%% box %s for %s.%s with pk %s %%}' % (name, app, model, new_pk)
    return update_one_box

def migrate_model(processor, model, fields):
    from ella.core.models import Publishable
    model = get_model(*model.split('.'))
    ct = ContentType.objects.get_for_model(model)
    if model == Publishable:
        ct = None
    print 'processing', model._meta, ':', 
    sys.stdout.flush()

    converted = 0
    deps = 0

    try:
        enter_transaction_management()
        managed(True)

        try:
            for m in model.objects.order_by().iterator():
                if not ct: # publishable
                    ct = ContentType.objects.get_for_id(m.content_type_id)
                sys.stdout.write('.')
                converted += 1

                # commit every 1000 iterations
                if (converted % 1000) == 0 and is_dirty():
                    commit()
                    sys.stdout.write('C')
                    sys.stdout.flush()

                dirty = False
                for f in fields:
                    val = getattr(m, f)
                    if val:
                        val, cnt = BOX_RE.subn(update_field(m, ct), val)
                        if cnt > 0:
                            deps += cnt
                            setattr(m, f, val)
                            dirty = True

                SourceText.objects.extract_from_instance(m, processor, fields, content_type=ct, force_save=dirty, force_create=True)
        except:
            # rollback and propagate if something goes wrong
            if is_dirty():
                rollback()
            raise
        else:
            # commit at the end
            if is_dirty():
                commit()
    finally:
        leave_transaction_management()

    print
    print 'DONE converted %d (%d reported dependencies)' % (converted, deps,)
    sys.stdout.flush()

def migrate_markup(processor, modelfields):
    create_id_lookup()

    for model, fields in modelfields:
        migrate_model(processor, model, fields)


class Command(NoArgsCommand):
    args = 'migrate_markup'
    help = '''migrate_markup:

    settings:

        MIGRATE_MARKUP_PROCESSOR = 'markdown'
        
        MIGRATE_MARKUP_FIELDS = [ 
            ('core.publishable', ['description','title']),
            ('article.articles', ['XXX',]),
        ]
    
    
    '''
    def handle(self, *args, **options):
        if not hasattr(settings, 'MIGRATE_MARKUP_FIELDS') or not hasattr(settings, 'MIGRATE_MARKUP_PROCESSOR'):
            print self.help
            return

        try:
            processor = TextProcessor.objects.get(name=settings.MIGRATE_MARKUP_PROCESSOR)
        except TextProcessor.DoesNotExist, e:
            print self.help
            return

        migrate_markup(processor, settings.MIGRATE_MARKUP_FIELDS)
        

