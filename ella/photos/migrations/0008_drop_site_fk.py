import datetime
from south.db import db
from django.db import models
from django.contrib.sites.models import Site
from ella.photos.models import *

class Migration:
    
    def forwards(self, orm):
        # Deleting field 'FormatedPhoto.filename'
        db.delete_column('photos_format', 'site_id')
        
    def backwards(self, orm):
        # Deleting field 'FormatedPhoto.filename'
        db.add_column('photos_format', 'site', models.ForeignKey(Site, null=False))
        
        
    
    
    models = {
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'db_table': "'django_site'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'photos.formatedphoto': {
            'Meta': {'unique_together': "(('photo','format'),)"},
            'crop_height': ('models.PositiveIntegerField', [], {}),
            'crop_left': ('models.PositiveIntegerField', [], {}),
            'crop_top': ('models.PositiveIntegerField', [], {}),
            'crop_width': ('models.PositiveIntegerField', [], {}),
            'format': ('models.ForeignKey', ["orm['photos.Format']"], {}),
            'height': ('models.PositiveIntegerField', [], {'editable': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'image': ('models.ImageField', [], {'height_field': "'height'", 'width_field': "'width'"}),
            'photo': ('models.ForeignKey', ["orm['photos.Photo']"], {}),
            'width': ('models.PositiveIntegerField', [], {'editable': 'False'})
        },
        'photos.photo': {
            'Meta': {'ordering': "('-created',)"},
            'authors': ('models.ManyToManyField', ["orm['core.Author']"], {'related_name': "'photo_set'", 'verbose_name': "_('Authors')"}),
            'created': ('models.DateTimeField', [], {'default': 'datetime.datetime.now', 'editable': 'False'}),
            'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
            'height': ('models.PositiveIntegerField', [], {'editable': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'image': ('models.ImageField', ["_('Image')"], {'height_field': "'height'", 'width_field': "'width'"}),
            'important_bottom': ('models.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'important_left': ('models.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'important_right': ('models.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'important_top': ('models.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'source': ('models.ForeignKey', ["orm['core.Source']"], {'null': 'True', 'verbose_name': "_('Source')", 'blank': 'True'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '200'}),
            'width': ('models.PositiveIntegerField', [], {'editable': 'False'})
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
            'sites': ('models.ManyToManyField', ["orm['sites.Site']"], {'verbose_name': "_('Sites')"}),
            'stretch': ('models.BooleanField', ["_('Stretch')"], {})
        },
        'core.source': {
            'Meta': {'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.author': {
            'Meta': {'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    complete_apps = ['photos']
