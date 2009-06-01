
import south
from south.db import db
from django.db import models

class Migration(object):
    def forwards(self, orm):
        print 'core', '0003_aaa', 'up'

    def backwards(self, orm):
        print 'core', '0003_aaa', 'down'

    models = {
    }

