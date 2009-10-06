
from south.db import db
from django.db import models
from ella.photos.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'FormatedPhoto.image'
        db.add_column('photos_formatedphoto', 'image', models.ImageField(height_field='height', width_field='width', max_length=300))
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'FormatedPhoto.image'
        db.delete_column('photos_formatedphoto', 'image')
