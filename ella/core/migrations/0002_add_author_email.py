
from south.db import db
from django.db import models
from ella.core.models import *

class Migration:
    
    def forwards(self):
        
        # Adding field 'Author.email'
        db.add_column('core_author', 'email', models.EmailField(_('Email'), blank=True))
        
    
    def backwards(self):
        
        # Deleting field 'Author.email'
        db.delete_column('core_author', 'email')
        
