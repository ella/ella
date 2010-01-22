
import datetime

from south.db import db
from django.db import models

from ella.core.migrations.base.base_0002 import BasePublishableDataMigration
from ella.core.migrations.base.base_0002 import alter_foreignkey_to_int, migrate_foreignkey


class Migration(BasePublishableDataMigration):
    models = dict.copy(BasePublishableDataMigration.models)
    models.update(
        {
            'discussions.topic': {
                'Meta': {'ordering': "('-created',)"},
                'created': ('models.DateTimeField', ["_('Created')"], {'default': 'datetime.datetime.now', 'editable': 'False'}),
                'publishable_ptr': ('models.OneToOneField', ["orm['core.Publishable']"], {}),
            },
        }
    )

    app_label = 'discussions'
    model = 'topic'
    table = '%s_%s' % (app_label, model)

    publishable_uncommon_cols = {
        'description': 'description',
    }

    def alter_self_foreignkeys(self, orm):
        # migrate new topic IDs to topicthread
        alter_foreignkey_to_int('discussions_topicthread', 'topic')

    def move_self_foreignkeys(self, orm):
        # migrate new topic IDs to topicthread
        migrate_foreignkey(self.app_label, self.model, 'discussions_topicthread', self.model, self.orm)

