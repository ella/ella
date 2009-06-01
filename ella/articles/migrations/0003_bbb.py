
import south
from south.db import db
from django.db import models

class Migration(object):
    depends_on = (
        ("core", "0003_bbb"),
    )

    def forwards(self, orm):
        print 'articles', '0003_bbb', 'up'

    def backwards(self, orm):
        print 'articles', '0003_bbb', 'down'

    models = {}

class Plugin(object):
    def forwards(self, orm):
        print 'articles', '0003_bbb', 'plugin', 'up'

    def backwards(self, orm):
        print 'articles', '0003_bbb', 'plugin', 'down'

p = Plugin()
k = ("core", "0003_bbb")

if not hasattr(south, 'plugins'):
    south.plugins = {}
if not south.plugins.has_key(k):
    south.plugins[k] = set()

south.plugins[k].add(p)

