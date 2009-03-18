
from south.db import db
from django.db import models
from djangobaselibrary.sample.models import *

'''
created via:
./djangobaseproject/manage.py startmigration sample add_spam_count --add-field Spam.count
'''

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'Spam.count'
        db.add_column('sample_spam', 'count', models.IntegerField(null=True))
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'Spam.count'
        db.delete_column('sample_spam', 'count')
        
    
    
    models = {
        
    }
    
    
