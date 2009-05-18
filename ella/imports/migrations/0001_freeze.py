
from south.db import db
from django.db import models
from ella.imports.models import *

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
