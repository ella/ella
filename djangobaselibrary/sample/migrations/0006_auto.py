
from south.db import db
from django.db import models
from djangobaselibrary.sample.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Changing field 'Spam.count'
        db.alter_column('sample_spam', 'count', models.IntegerField(null=True))
        
    
    
    def backwards(self, orm):
        
        # Changing field 'Spam.count'
        db.alter_column('sample_spam', 'count', models.IntegerField())
        
    
    
    models = {
        'sample.spam': {
            'Meta': {'unique_together': "(('name','expires'),)"},
            'count': ('models.IntegerField', [], {'null': 'True'}),
            'expires': ('models.DateTimeField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '255'}),
            'weight': ('models.FloatField', [], {})
        }
    }
    
    complete_apps = ['sample']
