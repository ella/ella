
from south.db import db
from django.db import models
from djangobaselibrary.sample.models import *

class Migration:
    def forwards(self, orm):
        # adding unique together meta
        db.create_index('sample_spam', ['name', 'expires'], unique=True)

    def backwards(self, orm):
        # removing unique together meta
        db.delete_index('sample_spam', ['name', 'expires'])

    models = {
        'sample.spam': {
            'Meta': {'unique_together': "(('name','expires'),)"},
            'count': ('models.IntegerField', [], {}),
            'expires': ('models.DateTimeField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '255'}),
            'weight': ('models.FloatField', [], {})
        }
    }

    complete_apps = ['sample']

