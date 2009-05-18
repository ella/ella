
from south.db import db
from django.db import models
from ella.galleries.models import *

class Migration:
    
    def forwards(self, orm):
        "Write your forwards migration here"
    
    
    def backwards(self, orm):
        "Write your backwards migration here"
    
    
    models = {
        'core.category': {
            'Meta': {'ordering': "('site','tree_path',)", 'unique_together': "(('site','tree_path'),)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'galleries.galleryitem': {
            'Meta': {'ordering': "('order',)", 'unique_together': "(('gallery','order',),)"},
            'gallery': ('models.ForeignKey', ["orm['galleries.Gallery']"], {'verbose_name': '_("Parent gallery")'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'order': ('models.IntegerField', ["_('Object order')"], {}),
            'target_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'verbose_name': "_('Target content type')"}),
            'target_id': ('models.IntegerField', ["_('Target ID')"], {'db_index': 'True'})
        },
        'galleries.gallery': {
            'category': ('models.ForeignKey', ["orm['core.Category']"], {'null': 'True', 'verbose_name': "_('Category')", 'blank': 'True'}),
            'content': ('models.TextField', ["_('Content')"], {'blank': 'True'}),
            'created': ('models.DateTimeField', ["_('Created')"], {'default': 'datetime.now', 'editable': 'False'}),
            'description': ('models.CharField', ["_('Description')"], {'max_length': '3000', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'owner': ('models.ForeignKey', ["orm['core.Author']"], {'null': 'True', 'verbose_name': "_('Gallery owner')", 'blank': 'True'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '255'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.author': {
            'Meta': {'ordering': "('name','slug',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    complete_apps = ['galleries']
