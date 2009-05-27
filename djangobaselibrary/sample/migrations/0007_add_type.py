
from south.db import db
from django.db import models
from djangobaselibrary.sample.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Type'
        db.create_table('sample_type', (
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(max_length=255)),
            ('description', models.TextField()),
        ))
        db.send_create_signal('sample', ['Type'])
        
        # Adding field 'Spam.type'
        db.add_column('sample_spam', 'type', models.ForeignKey(orm.Type))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Type'
        db.delete_table('sample_type')
        
        # Deleting field 'Spam.type'
        db.delete_column('sample_spam', 'type_id')
        
    
    
    models = {
        'sample.spam': {
            'Meta': {'unique_together': "(('name','expires'),)"},
            'count': ('models.IntegerField', [], {'null': 'True'}),
            'expires': ('models.DateTimeField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '255'}),
            'type': ('models.ForeignKey', ["orm['sample.Type']"], {}),
            'weight': ('models.FloatField', [], {})
        },
        'sample.type': {
            'description': ('models.TextField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '255'})
        }
    }
    
    complete_apps = ['sample']
