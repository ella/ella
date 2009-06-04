
from south.db import db
from django.db import models

from ella.hacks import south

class Migration:

    def forwards(self, orm):
        for p in south.plugins.get("core", "0002_03_move_publishable_data"):
            # migrate publishables
            p.forwards_publishable(orm)

            # migrate generic relations
            p.forwards_generic_relations(orm)

            # migrate placements
            p.forwards_placements(orm)

            # migrate related
            p.forwards_related(orm)

    def backwards(self, orm):
        print 'there is no way back'

    models = {
        'core.publishable': {
            'Meta': {'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
    }


