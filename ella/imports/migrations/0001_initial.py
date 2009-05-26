
from south.db import db
from django.db import models
from ella.imports.models import *

class Migration:
    
    depends_on = (
        ("core", "0001_initial"),
        ("photos", "0001_initial"),
        ("articles", "0001_initial"),
    )
 
    def forwards(self, orm):
        
        # Adding model 'ServerItem'
        db.create_table('imports_serveritem', (
            ('id', models.AutoField(primary_key=True)),
            ('server', models.ForeignKey(orm.Server)),
            ('title', models.CharField(_('Title'), max_length=100)),
            ('summary', models.TextField(_('Summary'))),
            ('updated', models.DateTimeField(_('Updated'))),
            ('priority', models.IntegerField(_('Priority'), default=0)),
            ('slug', models.SlugField(_('Slug'), max_length=255)),
            ('link', models.URLField(_('Link'), max_length=400, verify_exists=True)),
            ('photo_url', models.URLField(_('Image URL'), blank=True, max_length=400, verify_exists=False)),
            ('photo', models.ForeignKey(orm['photos.Photo'], null=True, verbose_name=_('Photo'), blank=True)),
        ))
        db.send_create_signal('imports', ['ServerItem'])
        
        # Adding model 'Server'
        db.create_table('imports_server', (
            ('id', models.AutoField(primary_key=True)),
            ('title', models.CharField(_('Title'), max_length=100)),
            ('domain', models.URLField(_('Domain'), verify_exists=False)),
            ('slug', models.SlugField(_('Slug'), max_length=255)),
            ('url', models.URLField(_('Atom URL'), blank=True, max_length=300, verify_exists=False)),
            ('category', models.ForeignKey(orm['core.Category'], null=True, verbose_name=_('Category'), blank=True)),
        ))
        db.send_create_signal('imports', ['Server'])
        
        # Creating unique_together for [server, slug] on ServerItem.
        db.create_unique('imports_serveritem', ['server_id', 'slug'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'ServerItem'
        db.delete_table('imports_serveritem')
        
        # Deleting model 'Server'
        db.delete_table('imports_server')
        
        # Deleting unique_together for [server, slug] on ServerItem.
        db.delete_unique('imports_serveritem', ['server_id', 'slug'])
        
    
    
    models = {
        'core.category': {
            'Meta': {'ordering': "('site','tree_path',)", 'unique_together': "(('site','tree_path'),)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'photos.photo': {
            'Meta': {'ordering': "('-created',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'imports.serveritem': {
            'Meta': {'ordering': "('-updated',)", 'unique_together': "(('server','slug',),)"},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'link': ('models.URLField', ["_('Link')"], {'max_length': '400', 'verify_exists': 'True'}),
            'photo': ('models.ForeignKey', ["orm['photos.Photo']"], {'null': 'True', 'verbose_name': "_('Photo')", 'blank': 'True'}),
            'photo_url': ('models.URLField', ["_('Image URL')"], {'blank': 'True', 'max_length': '400', 'verify_exists': 'False'}),
            'priority': ('models.IntegerField', ["_('Priority')"], {'default': '0'}),
            'server': ('models.ForeignKey', ["orm['imports.Server']"], {}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'summary': ('models.TextField', ["_('Summary')"], {}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '100'}),
            'updated': ('models.DateTimeField', ["_('Updated')"], {})
        },
        'imports.server': {
            'Meta': {'ordering': "('title',)"},
            'category': ('models.ForeignKey', ["orm['core.Category']"], {'null': 'True', 'verbose_name': "_('Category')", 'blank': 'True'}),
            'domain': ('models.URLField', ["_('Domain')"], {'verify_exists': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '100'}),
            'url': ('models.URLField', ["_('Atom URL')"], {'blank': 'True', 'max_length': '300', 'verify_exists': 'False'})
        }
    }
    
    complete_apps = ['imports']
