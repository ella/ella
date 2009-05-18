
from south.db import db
from django.db import models
from ella.catlocks.models import *

class Migration:
    
    def forwards(self, orm):
        "Write your forwards migration here"
    
    
    def backwards(self, orm):
        "Write your backwards migration here"
    
    
    models = {
        'core.category': {
            'Meta': {'ordering': "('site','tree_path',)", 'unique_together': "(('site','tree_path'),)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'catlocks.categorylock': {
            'category': ('CachedForeignKey', ["orm['core.Category']"], {'unique': 'True', 'verbose_name': "_('Category')"}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'password': ('models.CharField', ["_('Password')"], {'max_length': '255'})
        }
    }
    
    complete_apps = ['catlocks']
