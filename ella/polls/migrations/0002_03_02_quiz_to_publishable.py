
from south.db import db
from django.db import models

from ella.core.migrations.base.base_0002 import BasePublishableDataMigration
from ella.core.migrations.base.base_0002 import alter_foreignkey_to_int, migrate_foreignkey


class Migration(BasePublishableDataMigration):
    models = dict.copy(BasePublishableDataMigration.models)
    models.update(
        {
            'polls.quiz': {
                'Meta': {'ordering': "('-active_from',)", '_bases': ['ella.core.models.publishable.Publishable']},
                'active_from': ('models.DateTimeField', ["_('Active from')"], {}),
                'active_till': ('models.DateTimeField', ["_('Active till')"], {}),
                'has_correct_answers': ('models.BooleanField', ["_('Has correct answers')"], {}),
                'publishable_ptr': ('models.OneToOneField', ["orm['core.Publishable']"], {}),
                'text': ('models.TextField', ["_('Text')"], {}),
                'text_announcement': ('models.TextField', ["_('Text with announcement')"], {}),
                'text_results': ('models.TextField', ["_('Text with results')"], {})
            },
        }
    )

    app_label = 'polls'
    model = 'quiz'
    table = '%s_%s' % (app_label, model)

    publishable_uncommon_cols = {
        'description': 'text_announcement'
    }
    
    def alter_self_foreignkeys(self, orm):
        # migrate authors as in base
        super(Migration, self).alter_self_foreignkeys(orm)
        alter_foreignkey_to_int('polls_question', 'quiz', null=True)
        alter_foreignkey_to_int('polls_result', 'quiz')

    def move_self_foreignkeys(self, orm):
        # migrate authors as in base
        super(Migration, self).move_self_foreignkeys(orm)
        # migrate new quiz IDs to question
        migrate_foreignkey(self.app_label, self.model, 'polls_question', self.model, self.orm, null=True)
        # migrate new quiz IDs to results
        migrate_foreignkey(self.app_label, self.model, 'polls_result', self.model, self.orm)

