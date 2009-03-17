
from south.db import db
from django.db import models
from djangobaselibrary.sample.models import *

'''
created via:
./djangobaseproject/manage.py startmigration sample create_spam --model Spam
'''

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Spam'
        db.create_table('sample_spam', (
            ('expires', models.DateTimeField()),
            ('id', models.AutoField(primary_key=True)),
            ('weight', models.FloatField()),
            ('name', models.CharField(max_length=255)),
        ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Spam'
        db.delete_table('sample_spam')
        
    
    
    models = {
        
    }
    
    
