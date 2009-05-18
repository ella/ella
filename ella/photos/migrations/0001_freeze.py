
from south.db import db
from django.db import models
from ella.photos.models import *

class Migration:
    
    def forwards(self, orm):
        "Write your forwards migration here"
    
    
    def backwards(self, orm):
        "Write your backwards migration here"
    
    
    models = {
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'db_table': "'django_site'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'photos.format': {
            'Meta': {'ordering': "('name','-max_width',)"},
            'flexible_height': ('models.BooleanField', ["_('Flexible height')"], {}),
            'flexible_max_height': ('models.PositiveIntegerField', ["_('Flexible max height')"], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'max_height': ('models.PositiveIntegerField', ["_('Max height')"], {}),
            'max_width': ('models.PositiveIntegerField', ["_('Max width')"], {}),
            'name': ('models.CharField', ["_('Name')"], {'max_length': '80'}),
            'nocrop': ('models.BooleanField', ["_('Do not crop')"], {}),
            'resample_quality': ('models.IntegerField', ["_('Resample quality')"], {'default': '85'}),
            'site': ('models.ForeignKey', ["orm['sites.Site']"], {}),
            'stretch': ('models.BooleanField', ["_('Stretch')"], {})
        },
        'photos.photo': {
            'Meta': {'ordering': "('-created',)"},
            'authors': ('models.ManyToManyField', ["orm['core.Author']"], {'related_name': "'photo_set'", 'verbose_name': "_('Authors')"}),
            'created': ('models.DateTimeField', [], {'default': 'datetime.now', 'editable': 'False'}),
            'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
            'height': ('models.PositiveIntegerField', [], {'editable': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'image': ('models.ImageField', [], {'height_field': "'height'", 'width_field': "'width'"}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'source': ('models.ForeignKey', ["orm['core.Source']"], {'null': 'True', 'verbose_name': "_('Source')", 'blank': 'True'}),
            'tags': '<< PUT FIELD DEFINITION HERE >>',
            'title': ('models.CharField', ["_('Title')"], {'max_length': '200'}),
            'width': ('models.PositiveIntegerField', [], {'editable': 'False'})
        },
        'photos.formatedphoto': {
            'Meta': {'unique_together': "(('photo','format'),)"},
            'crop_height': ('models.PositiveIntegerField', [], {}),
            'crop_left': ('models.PositiveIntegerField', [], {}),
            'crop_top': ('models.PositiveIntegerField', [], {}),
            'crop_width': ('models.PositiveIntegerField', [], {}),
            'filename': ('models.CharField', [], {'max_length': '300', 'editable': 'False'}),
            'format': ('models.ForeignKey', ["orm['photos.Format']"], {}),
            'height': ('models.PositiveIntegerField', [], {'editable': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'photo': ('models.ForeignKey', ["orm['photos.Photo']"], {}),
            'width': ('models.PositiveIntegerField', [], {'editable': 'False'})
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
    
    complete_apps = ['photos']
