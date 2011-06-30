
from south.db import db
from django.db import models

from ella.core.migrations.base.base_0002 import BasePublishableDataMigration
from ella.core.migrations.base.base_0002 import alter_foreignkey_to_int, migrate_foreignkey


class Migration(BasePublishableDataMigration):
    models = dict.copy(BasePublishableDataMigration.models)
    models.update(
        {
            'series.serie': {
                'Meta': {'_bases': ['ella.core.models.publishable.Publishable']},
                'finished': ('models.DateField', ["_('Finished')"], {'null': 'True', 'blank': 'True'}),
                'hide_newer_parts': ('models.BooleanField', ["_('Hide newer parts')"], {'default': 'False'}),
                'publishable_ptr': ('models.OneToOneField', ["orm['core.Publishable']"], {}),
                'started': ('models.DateField', ["_('Started')"], {}),
                'text': ('models.TextField', ["_('Text')"], {})
            },
        }
    )

    app_label = 'series'
    model = 'serie'
    table = '%s_%s' % (app_label, model)
    publishable_uncommon_cols = {
        'description': 'perex',
    }

    def alter_self_foreignkeys(self, orm):
        alter_foreignkey_to_int('series_seriepart', 'serie')

    def move_self_foreignkeys(self, orm):
        # migrate new serie IDs to seriepart
        migrate_foreignkey(self.app_label, self.model, 'series_seriepart', self.model, self.orm)

    def forwards(self, orm):
        db.rename_column('series_serie', 'description', 'text')
        BasePublishableDataMigration().forwards(orm)

