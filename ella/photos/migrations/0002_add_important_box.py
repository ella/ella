
from south.db import db
from django.db import models
from ella.photos.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'Photo.important_right'
        db.add_column('photos_photo', 'important_right', models.PositiveIntegerField(null=True, blank=True))
        
        # Adding field 'Photo.important_left'
        db.add_column('photos_photo', 'important_left', models.PositiveIntegerField(null=True, blank=True))
        
        # Adding field 'Photo.important_top'
        db.add_column('photos_photo', 'important_top', models.PositiveIntegerField(null=True, blank=True))
        
        # Adding field 'Photo.important_bottom'
        db.add_column('photos_photo', 'important_bottom', models.PositiveIntegerField(null=True, blank=True))
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'Photo.important_right'
        db.delete_column('photos_photo', 'important_right')
        
        # Deleting field 'Photo.important_left'
        db.delete_column('photos_photo', 'important_left')
        
        # Deleting field 'Photo.important_top'
        db.delete_column('photos_photo', 'important_top')
        
        # Deleting field 'Photo.important_bottom'
        db.delete_column('photos_photo', 'important_bottom')
        
