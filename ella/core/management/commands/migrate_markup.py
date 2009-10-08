import re

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import NoArgsCommand
from django.conf import settings
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
        Dependency.objects.get_or_create(
                dependent_ct=content_type,
                dependent_id=instance.pk,

                target_ct=ct,
                target_id=new_pk
            )
        if new_pk != pk:
            print '-',
        else:
            print '#',

        # put everything together
        return '{%% box %s for %s.%s with pk %s %%}' % (name, app, model, pk)
    return update_one_box

def migrate_markup(processor, modelfields):
    create_id_lookup()

    for model, fields in modelfields:
        model = get_model(*model.split('.'))
        ct = ContentType.objects.get_for_model(model)
        print 'processing', model._meta, ':', 

        for m in model.objects.all():
            print '.',
            dirty = False
            for f in fields:
                val = getattr(m, f)
                if val:
                    val, cnt = BOX_RE.subn(update_field(m, ct), val)
                    if cnt > 0:
                        setattr(m, f, val)
                        dirty = True

            SourceText.objects.extract_from_instance(m, processor, fields, content_type=ct, force_save=dirty)
        print
        print 'DONE'


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
        

