
from south.db import db
from django.db import models

from ella.core.migrations.base.base_0002 import BasePublishableDataMigration
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

    app_label = 'polls'
    model = 'contest'
    table = '%s_%s' % (app_label, model)

    publishable_uncommon_cols = {
        'description': 'text_announcement'
    }

    def alter_self_foreignkeys(self, orm):
        alter_foreignkey_to_int('polls_question', 'contest', models.IntegerField(blank=True, null=True))
        alter_foreignkey_to_int('polls_contestant', 'contest', models.IntegerField(blank=True))

    def move_self_foreignkeys(self, orm):
        # migrate new contest IDs to question
        migrate_foreignkey(self.app_label, self.model, 'polls_question', self.model, self.orm, null=True)
        # migrate new contest IDs to contestant
        migrate_foreignkey(self.app_label, self.model, 'polls_contestant', self.model, self.orm)

