
from south.db import db
from django.db import models

from ella.hacks import south

from ella.media.models import *

from ella.core.migrations.base.base_0002 import BasePublishableDataMigration, BasePublishableDataPlugin
from ella.core.migrations.base.base_0002 import alter_foreignkey_to_int, migrate_foreignkey


class Migration(BasePublishableDataMigration):
    models = dict.copy(BasePublishableDataMigration.models)
    models.update(
        {
            'media.media': {
                'Meta': {'_bases': ['ella.core.models.publishable.Publishable']},
                'created': ('models.DateTimeField', ["_('Created')"], {'default': 'datetime.now', 'editable': 'False'}),
                'file': ('MediaField', [], {}),
                'publishable_ptr': ('models.OneToOneField', ["orm['core.Publishable']"], {}),
                'text': ('models.TextField', ["_('Content')"], {'blank': 'True'}),
                'updated': ('models.DateTimeField', ["_('Updated')"], {'null': 'True', 'blank': 'True'})
            },
        }
    )


class Plugin(BasePublishableDataPlugin):
    migration = Migration

    app_label = 'media'
    model = 'media'
    table = '%s_%s' % (app_label, model)

    publishable_uncommon_cols = {
        'source_id': 'source_id',
        'description': 'description',
    }

    def alter_self_foreignkeys(self, orm):
        # migrate authors as in base
        super(Plugin, self).alter_self_foreignkeys(orm)
        alter_foreignkey_to_int('media_section', 'media')
        alter_foreignkey_to_int('media_usage', 'media')

    def move_self_foreignkeys(self, orm):
        # migrate authors as in base
        super(Plugin, self).move_self_foreignkeys(orm)
        # migrate new media IDs to section
        migrate_foreignkey(self.app_label, self.model, 'media_section', self.model, self.orm)
        # migrate new media IDs to usage
        migrate_foreignkey(self.app_label, self.model, 'media_usage', self.model, self.orm)

south.plugins.register("core", "0002_03_move_publishable_data", Plugin())
