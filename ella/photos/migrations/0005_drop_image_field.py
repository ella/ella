
from south.db import db
from django.db import models
from ella.photos.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Deleting field 'FormatedPhoto.filename'
        db.delete_column('photos_formatedphoto', 'filename')
        
    
    
    def backwards(self, orm):
        
        # Adding field 'FormatedPhoto.filename'
        db.add_column('photos_formatedphoto', 'filename', models.CharField(max_length=300, editable=False))
        
