
from south.db import db
from django.db import models
from ella.ellaadmin.models import *

class Migration:
    
    depends_on = (
        ("core", "0001_initial"),
    )
 
    def forwards(self, orm):
        "Write your forwards migration here"
    
    
    def backwards(self, orm):
        "Write your backwards migration here"
    
    
    models = {
        
    }
    
    complete_apps = ['ellaadmin']
