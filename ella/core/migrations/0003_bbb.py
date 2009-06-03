
import south
from south.db import db
from django.db import models

from ella.hacks import south


class Migration(object):
    def forwards(self, orm):
        print 'core', '0003_bbb', 'up'
        print orm.publishable
        for p in south.plugins.get("core", "0003_bbb"):
            p.forwards(orm)

    def backwards(self, orm):
        print 'core', '0003_bbb', 'down'
        print orm.publishable
        for p in south.plugins.get("core", "0003_bbb"):
            p.backwards(orm)

    models = {
        'core.publishable': {
            'Meta': {'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
    }

