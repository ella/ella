from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from django.core.management import call_command

from south.db import db
from django.db import models
from ella.core.models import *

class Migration:
    
    def forwards(self):
        
        # Adding field 'Publishable.publish_from'
        db.add_column('core_publishable', 'publish_from', models.DateTimeField(editable=False, default=datetime(3000, 1, 1)))
        call_command('update_publishable_publish_from')
        
    
    def backwards(self):
        
        # Deleting field 'Publishable.publish_from'
        db.delete_column('core_publishable', 'publish_from')
        
