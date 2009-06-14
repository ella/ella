
from south.db import db
from django.db import models

from ella.hacks import south

from ella.core.migrations.base.base_0002 import BasePublishableDataMigration, BasePublishableDataPlugin
from ella.core.migrations.base.base_0002 import alter_foreignkey_to_int, migrate_foreignkey


class Migration(BasePublishableDataMigration):
    models = dict.copy(BasePublishableDataMigration.models)
    models.update(
        {
            'polls.contest': {
                'Meta': {'ordering': "('-active_from',)", '_bases': ['ella.core.models.publishable.Publishable']},
                'active_from': ('models.DateTimeField', ["_('Active from')"], {}),
                'active_till': ('models.DateTimeField', ["_('Active till')"], {}),
                'publishable_ptr': ('models.OneToOneField', ["orm['core.Publishable']"], {}),
                'text': ('models.TextField', ["_('Text')"], {}),
                'text_announcement': ('models.TextField', ["_('Text with announcement')"], {}),
                'text_results': ('models.TextField', ["_('Text with results')"], {})
            },
        }
    )

class Plugin(BasePublishableDataPlugin):
    migration = Migration

    app_label = 'polls'
    model = 'contest'
    table = '%s_%s' % (app_label, model)

    publishable_uncommon_cols = {}
    
    def alter_self_foreignkeys(self, orm):
        alter_foreignkey_to_int('polls_question', 'contest')
        alter_foreignkey_to_int('polls_contestant', 'contest')

    def move_self_foreignkeys(self, orm):
        # migrate new contest IDs to question
        migrate_foreignkey(self.app_label, self.model, 'polls_question', self.model, self.orm)
        # migrate new contest IDs to contestant
        migrate_foreignkey(self.app_label, self.model, 'polls_contestant', self.model, self.orm)

south.plugins.register("core", "0002_03_move_publishable_data", Plugin())
