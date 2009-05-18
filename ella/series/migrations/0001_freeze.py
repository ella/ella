
from south.db import db
from django.db import models
from ella.series.models import *

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
        'series.serie': {
            'category': ('models.ForeignKey', ["orm['core.Category']"], {'verbose_name': "_('Category')"}),
            'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
            'finished': ('models.DateField', ["_('Finished')"], {'null': 'True', 'blank': 'True'}),
            'hide_newer_parts': ('models.BooleanField', ["_('Hide newer parts')"], {'default': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'perex': ('models.TextField', ["_('Perex')"], {}),
            'photo': ('models.ForeignKey', ["orm['photos.Photo']"], {'null': 'True', 'verbose_name': "_('Photo')", 'blank': 'True'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'unique': 'True'}),
            'started': ('models.DateField', ["_('Started')"], {}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '96'})
        },
        'core.placement': {
            'Meta': {'ordering': "('-publish_from',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'series.seriepart': {
            'Meta': {'ordering': "('serie','placement__publish_from',)"},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'part_no': ('models.PositiveSmallIntegerField', ["_('Part no.')"], {'default': '1', 'editable': 'False'}),
            'placement': ('CachedForeignKey', ["orm['core.Placement']"], {'unique': 'True'}),
            'serie': ('CachedForeignKey', ["orm['series.Serie']"], {'verbose_name': "_('Serie')"})
        },
        'photos.photo': {
            'Meta': {'ordering': "('-created',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    complete_apps = ['series']
