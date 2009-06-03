
import south
from south.db import db
from django.db import models

from ella.hacks import south


class Migration(object):
    depends_on = (
        ("core", "0003_bbb"),
    )

    def forwards(self, orm):
        print 'articles', '0003_bbb', 'up'

    def backwards(self, orm):
        print 'articles', '0003_bbb', 'down'

    models = {
        'core.publishable': {
            'Meta': {'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'articles.article': {
            'Meta': {'ordering': "('-created',)", '_bases': ['ella.core.models.publishable.Publishable']},
            'created': ('models.DateTimeField', ["_('Created')"], {'default': 'datetime.datetime.now', 'editable': 'False', 'db_index': 'True'}),
            'publishable_ptr': ('models.OneToOneField', ["orm['core.Publishable']"], {}),
            'updated': ('models.DateTimeField', ["_('Updated')"], {'null': 'True', 'blank': 'True'}),
            'upper_title': ('models.CharField', ["_('Upper title')"], {'max_length': '255', 'blank': 'True'})
        },
    }


class Plugin(object):
    @property
    def orm(self):
        return Migration.orm

    def forwards(self, orm):
        print 'articles', '0003_bbb', 'plugin', 'up'
        print self.orm.article

    def backwards(self, orm):
        print 'articles', '0003_bbb', 'plugin', 'down'
        print self.orm.article

south.plugin.register("core", "0003_bbb", Plugin())

