
from south.db import db
from django.db import models
from ella.catlocks.models import *

class Migration:
    
    depends_on = (
        ("core", "0001_initial"),
    )
 
    def forwards(self, orm):
        
        # Adding model 'CategoryLock'
        db.create_table('catlocks_categorylock', (
            ('id', models.AutoField(primary_key=True)),
            ('category', CachedForeignKey(orm['core.Category'], unique=True, verbose_name=_('Category'))),
            ('password', models.CharField(_('Password'), max_length=255)),
        ))
        db.send_create_signal('catlocks', ['CategoryLock'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'CategoryLock'
        db.delete_table('catlocks_categorylock')
        
    
    
    models = {
        'core.category': {
            'Meta': {'ordering': "('site','tree_path',)", 'unique_together': "(('site','tree_path'),)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'catlocks.categorylock': {
            'category': ('CachedForeignKey', ["orm['core.Category']"], {'unique': 'True', 'verbose_name': "_('Category')"}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'password': ('models.CharField', ["_('Password')"], {'max_length': '255'})
        }
    }
    
    complete_apps = ['catlocks']
