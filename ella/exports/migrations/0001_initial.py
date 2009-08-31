
from south.db import db
from django.db import models
from ella.exports.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'ExportPosition'
        db.create_table('exports_exportposition', (
            ('id', models.AutoField(primary_key=True)),
            ('visible_from', models.DateTimeField()),
            ('visible_to', models.DateTimeField(null=True, blank=True)),
            ('position', models.IntegerField(default=0, blank=True)),
            ('object', models.ForeignKey(orm.ExportMeta)),
            ('export', models.ForeignKey(orm.Export)),
        ))
        db.send_create_signal('exports', ['ExportPosition'])
        
        # Adding model 'Export'
        db.create_table('exports_export', (
            ('id', models.AutoField(primary_key=True)),
            ('category', models.ForeignKey(orm['core.Category'])),
            ('title', models.CharField(_('Title'), max_length=255)),
            ('slug', models.SlugField(_('Slug'), max_length=255)),
            ('max_visible_items', models.IntegerField(_('Maximum Visible Items'))),
            ('photo_format', models.ForeignKey(orm['photos.Format'])),
        ))
        db.send_create_signal('exports', ['Export'])
        
        # Adding model 'ExportMeta'
        db.create_table('exports_exportmeta', (
            ('id', models.AutoField(primary_key=True)),
            ('publishable', models.ForeignKey(orm['core.Publishable'])),
            ('title', models.CharField(_('Title'), max_length=64, blank=True)),
            ('photo', models.ForeignKey(orm['photos.Photo'], null=True, blank=True)),
            ('description', models.TextField(_('Description'), blank=True)),
        ))
        db.send_create_signal('exports', ['ExportMeta'])
        
        # Creating unique_together for [slug] on Export.
        db.create_unique('exports_export', ['slug'])
        
        # Creating unique_together for [title] on Export.
        db.create_unique('exports_export', ['title'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'ExportPosition'
        db.delete_table('exports_exportposition')
        
        # Deleting model 'Export'
        db.delete_table('exports_export')
        
        # Deleting model 'ExportMeta'
        db.delete_table('exports_exportmeta')
        
        # Deleting unique_together for [slug] on Export.
        db.delete_unique('exports_export', ['slug'])
        
        # Deleting unique_together for [title] on Export.
        db.delete_unique('exports_export', ['title'])
        
    
    
    models = {
        'core.category': {
            'Meta': {'unique_together': "(('site','tree_path'),)", 'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'photos.format': {
            'Meta': {'ordering': "('name','-max_width',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'photos.photo': {
            'Meta': {'ordering': "('-created',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'exports.exportposition': {
            'export': ('models.ForeignKey', ["orm['exports.Export']"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'object': ('models.ForeignKey', ["orm['exports.ExportMeta']"], {}),
            'position': ('models.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'visible_from': ('models.DateTimeField', [], {}),
            'visible_to': ('models.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'exports.export': {
            'Meta': {'unique_together': "(('title',),('slug',))"},
            'category': ('models.ForeignKey', ["orm['core.Category']"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'max_visible_items': ('models.IntegerField', ["_('Maximum Visible Items')"], {}),
            'photo_format': ('models.ForeignKey', ["orm['photos.Format']"], {}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '255'})
        },
        'core.publishable': {
            'Meta': {'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'exports.exportmeta': {
            'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'photo': ('models.ForeignKey', ["orm['photos.Photo']"], {'null': 'True', 'blank': 'True'}),
            'publishable': ('models.ForeignKey', ["orm['core.Publishable']"], {}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '64', 'blank': 'True'})
        }
    }
    
    complete_apps = ['exports']
