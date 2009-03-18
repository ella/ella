
from south.db import db
from django.db import models
from djangobaselibrary.sample.models import *

'''
created via:
./djangobaseproject/manage.py startmigration sample freeze --freeze sample
'''

class Migration:
    
    def forwards(self, orm):
        "Write your forwards migration here"
    
    
    def backwards(self, orm):
        "Write your backwards migration here"
    
    
    models = {
        'sample.spam': {
            'count': ('models.IntegerField', [], {}),
            'expires': ('models.DateTimeField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '255'}),
            'weight': ('models.FloatField', [], {})
        }
    }
    
    complete_apps = ['sample']
