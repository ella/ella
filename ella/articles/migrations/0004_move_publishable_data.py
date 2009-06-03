
from south.db import db
from django.db import models
from ella.articles.models import *

class Migration:
    depends_on = (
        ('core', '0004_move_publishable_data'),
    )
    def forwards(self, orm):
        pass
    def backwards(self, orm):
        pass
    models = {}


from ella.core.migrations_base import BasePublishableDataMigration
from ella.core.migrations_base import alter_foreignkey_to_int, migrate_foreignkey


class Plugin(BasePublishableDataMigration):

    app_label = 'articles'
    model = 'article'
    table = '%s_%s' % (app_label, model)

    publishable_uncommon_cols = {
        'source_id': 'source_id',
        'description': 'perex',
    }

    def alter_self_foreignkeys(self, orm):
        # migrate authors as in base
        super(Migration, self).alter_self_foreignkeys(orm)
        # migrate new article IDs to articlecontents
        alter_foreignkey_to_int('articles_articlecontents', 'article')
        # migrate new article IDs to oldrecipearticleredirect
        alter_foreignkey_to_int('recipes_oldrecipearticleredirect', 'new_id')
        # TODO: maybe foreginkyes should be taken from freeze orm

    def move_self_foreignkeys(self, orm):
        # migrate authors as in base
        super(Migration, self).move_self_foreignkeys(orm)
        # migrate new article IDs to articlecontents
        migrate_foreignkey(self.app_label, self.model, 'articles_articlecontents', self.model, orm)
        # migrate new article IDs to oldrecipearticleredirect
        migrate_foreignkey(self.app_label, self.model, 'recipes_oldrecipearticleredirect', 'new_id', orm)

    models = dict.copy(BasePublishableDataMigration.models)
    models.update({
        'articles.article': {
            'Meta': {'ordering': "('-created',)", '_bases': ['ella.core.models.publishable.Publishable']},
            'created': ('models.DateTimeField', ["_('Created')"], {'default': 'datetime.now', 'editable': 'False', 'db_index': 'True'}),
            'publishable_ptr': ('models.OneToOneField', ["orm['core.Publishable']"], {}),
            'updated': ('models.DateTimeField', ["_('Updated')"], {'null': 'True', 'blank': 'True'}),
            'upper_title': ('models.CharField', ["_('Upper title')"], {'max_length': '255', 'blank': 'True'})
        },
    })

