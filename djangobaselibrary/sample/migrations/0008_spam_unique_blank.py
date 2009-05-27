
from south.db import db
from django.db import models
from djangobaselibrary.sample.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Changing field 'Spam.count'
        db.alter_column('sample_spam', 'count', models.IntegerField(null=True, blank=True))
        
        # Changing field 'Type.description'
        db.alter_column('sample_type', 'description', models.TextField(null=True, blank=True))
        
        # Changing field 'Type.name'
        db.alter_column('sample_type', 'name', models.CharField(unique=True, max_length=255))
        
    
    
    def backwards(self, orm):
        
        # Changing field 'Spam.count'
        db.alter_column('sample_spam', 'count', models.IntegerField(null=True))
        
        # Changing field 'Type.description'
        db.alter_column('sample_type', 'description', models.TextField())
        
        # Changing field 'Type.name'
        db.alter_column('sample_type', 'name', models.CharField(max_length=255))
        
    
    
    models = {
        'sample.spam': {
            'Meta': {'unique_together': "(('name','expires'),)"},
            'count': ('models.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'expires': ('models.DateTimeField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '255'}),
            'type': ('models.ForeignKey', ["orm['sample.Type']"], {}),
            'weight': ('models.FloatField', [], {})
        },
        'sample.type': {
            'description': ('models.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }
    
    complete_apps = ['sample']
