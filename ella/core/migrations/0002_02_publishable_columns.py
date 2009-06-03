
from south.db import db
from django.db import models
from ella.core.models import *

class Migration:

    def forwards(self, orm):
        # add a temporary column on core_publishable to remember the old ID
        db.add_column('core_publishable', 'old_id', models.IntegerField(null=True))

    def backwards(self, orm):
        # drop temporary column
        db.delete_column('core_publishable', 'old_id')

    models = {
        'core.publishable': {
            'Meta': {'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
    }

