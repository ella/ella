
from south.db import db
from django.db import models
from django.conf import settings

from ella.core.migrations.base.base_0002 import BasePublishableDataMigration
from ella.core.migrations.base.base_0002 import alter_foreignkey_to_int, migrate_foreignkey

import datetime


class Migration(BasePublishableDataMigration):
    # TODO:
    # this is only temporary, it should be constructed dynamically
    # from each migration in installed_apps, that contains run_before
#    _depends_on = (
#        ('recepty.recipes', 'recipes', '0001_initial'),
#    )
#    depends_on = []
#    for app, label, migration in _depends_on:
#        if app in settings.INSTALLED_APPS:
#            depends_on.append((label, migration))

    models = dict.copy(BasePublishableDataMigration.models)
    models.update(
        {
            'articles.article': {
                'Meta': {'ordering': "('-created',)", '_bases': ['ella.core.models.publishable.Publishable']},
                'created': ('models.DateTimeField', ["_('Created')"], {'default': 'datetime.datetime.now', 'editable': 'False', 'db_index': 'True'}),
                'publishable_ptr': ('models.OneToOneField', ["orm['core.Publishable']"], {}),
                'updated': ('models.DateTimeField', ["_('Updated')"], {'null': 'True', 'blank': 'True'}),
                'upper_title': ('models.CharField', ["_('Upper title')"], {'max_length': '255', 'blank': 'True'})
            },
        }
    )

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
        if 'recepty.recipes' in settings.INSTALLED_APPS:
            # TODO: this should be solved via plugins
            alter_foreignkey_to_int('recipes_oldrecipearticleredirect', 'new_id')

    def move_self_foreignkeys(self, orm):
        # migrate authors as in base
        super(Migration, self).move_self_foreignkeys(orm)
        # migrate new article IDs to articlecontents
        migrate_foreignkey(self.app_label, self.model, 'articles_articlecontents', self.model, self.orm)
        if 'recepty.recipes' in settings.INSTALLED_APPS:
            # migrate new article IDs to oldrecipearticleredirect
            migrate_foreignkey(self.app_label, self.model, 'recipes_oldrecipearticleredirect', 'new_id', self.orm)

