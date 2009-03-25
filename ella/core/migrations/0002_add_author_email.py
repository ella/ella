from django.utils.translation import ugettext_lazy as _

from south.db import db
from django.db import models
from ella.core.models import *

class Migration:
    
    def forwards(self):
        
        # FIXME: remove null=True, because its in migration only (otherwise it does not run on sqlite)
        # Adding field 'Author.email'
        db.add_column('core_author', 'email', models.EmailField(_('Email'), blank=True, null=True))
        
    
    def backwards(self):
        
        # Deleting field 'Author.email'
        db.delete_column('core_author', 'email')
        
