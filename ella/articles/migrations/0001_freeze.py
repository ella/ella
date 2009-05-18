
from south.db import db
from django.db import models
from ella.articles.models import *

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
        'articles.articlecontents': {
            'article': ('models.ForeignKey', ["orm['articles.Article']"], {'verbose_name': "_('Article')"}),
            'content': ('models.TextField', ["_('Content')"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '200', 'blank': 'True'})
        },
        'articles.infobox': {
            'Meta': {'ordering': "('-created',)"},
            'content': ('models.TextField', ["_('Content')"], {}),
            'created': ('models.DateTimeField', ["_('Created')"], {'default': 'datetime.now', 'editable': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '255'}),
            'updated': ('models.DateTimeField', ["_('Updated')"], {'null': 'True', 'blank': 'True'})
        },
        'photos.photo': {
            'Meta': {'ordering': "('-created',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'articles.article': {
            'Meta': {'ordering': "('-created',)"},
            'authors': ('models.ManyToManyField', ["orm['core.Author']"], {'verbose_name': "_('Authors')"}),
            'category': ('models.ForeignKey', ["orm['core.Category']"], {'verbose_name': "_('Category')"}),
            'created': ('models.DateTimeField', ["_('Created')"], {'default': 'datetime.now', 'editable': 'False', 'db_index': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'perex': ('models.TextField', ["_('Perex')"], {}),
            'photo': ('models.ForeignKey', ["orm['photos.Photo']"], {'null': 'True', 'verbose_name': "_('Photo')", 'blank': 'True'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'source': ('models.ForeignKey', ["orm['core.Source']"], {'null': 'True', 'verbose_name': "_('Source')", 'blank': 'True'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '255'}),
            'updated': ('models.DateTimeField', ["_('Updated')"], {'null': 'True', 'blank': 'True'}),
            'upper_title': ('models.CharField', ["_('Upper title')"], {'max_length': '255', 'blank': 'True'})
        },
        'core.source': {
            'Meta': {'ordering': "('name',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.author': {
            'Meta': {'ordering': "('name','slug',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    complete_apps = ['articles']
