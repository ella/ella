
from south.db import db
from django.db import models
from ella.sendmail.models import *

class Migration:
    
    def forwards(self, orm):
        "Write your forwards migration here"
    
    
    def backwards(self, orm):
        "Write your backwards migration here"
    
    
    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'sendmail.mail': {
            'content': ('models.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'recipient': ('models.EmailField', [], {}),
            'sender': ('models.EmailField', [], {}),
            'sent': ('models.DateTimeField', [], {'default': 'datetime.datetime(2009, 5, 18, 19, 15, 58, 325193)'}),
            'target_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'verbose_name': "_('content type')"}),
            'target_id': ('models.PositiveIntegerField', ["_('target id')"], {'db_index': 'True'})
        }
    }
    
    complete_apps = ['sendmail']
