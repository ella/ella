
from south.db import db
from django.db import models
from django.contrib.sites.models import Site
from ella.photos.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding ManyToManyField 'Format.sites'
        db.create_table('photos_format_sites', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('format', models.ForeignKey(Format, null=False)),
            ('site', models.ForeignKey(Site, null=False))
        ))
        
    
    
    def backwards(self, orm):
        
        # Dropping ManyToManyField 'Format.sites'
        db.delete_table('photos_format_sites')
        
    
