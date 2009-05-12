
from south.db import db
from django.db import models
from ella.photos.models import *

class Migration:
    
    depends_on = (
        ("core", "0001_initial"),
    )
    
    def forwards(self, orm):
        
        # Adding model 'Photo'
        db.create_table('photos_photo', (
            ('description', models.TextField(_('Description'), blank=True)),
            ('title', models.CharField(_('Title'), max_length=200)),
            ('image', models.ImageField(height_field='height', width_field='width', upload_to=UPLOAD_TO)),
            ('created', models.DateTimeField(default=datetime.now, editable=False)),
            ('slug', models.SlugField(_('Slug'), max_length=255)),
            ('width', models.PositiveIntegerField(editable=False)),
            ('height', models.PositiveIntegerField(editable=False)),
            ('important_top', models.PositiveIntegerField(null=True, blank=True)),
            ('important_left', models.PositiveIntegerField(null=True, blank=True)),
            ('important_bottom', models.PositiveIntegerField(null=True, blank=True)),
            ('important_right', models.PositiveIntegerField(null=True, blank=True)),
            ('source', models.ForeignKey(orm['core.Source'], null=True, verbose_name=_('Source'), blank=True)),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('photos', ['Photo'])
        
        # Adding model 'FormatedPhoto'
        db.create_table('photos_formatedphoto', (
            ('crop_top', models.PositiveIntegerField()),
            ('crop_left', models.PositiveIntegerField()),
            ('photo', models.ForeignKey(orm.Photo)),
            ('format', models.ForeignKey(orm.Format)),
            ('crop_width', models.PositiveIntegerField()),
            ('filename', models.CharField(max_length=300, editable=False)),
            ('height', models.PositiveIntegerField(editable=False)),
            ('width', models.PositiveIntegerField(editable=False)),
            ('crop_height', models.PositiveIntegerField()),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('photos', ['FormatedPhoto'])
        
        # Adding model 'Format'
        db.create_table('photos_format', (
            ('name', models.CharField(_('Name'), max_length=80)),
            ('stretch', models.BooleanField(_('Stretch'))),
            ('flexible_max_height', models.PositiveIntegerField(_('Flexible max height'), null=True, blank=True)),
            ('site', models.ForeignKey(orm['sites.Site'])),
            ('max_height', models.PositiveIntegerField(_('Max height'))),
            ('nocrop', models.BooleanField(_('Do not crop'))),
            ('flexible_height', models.BooleanField(_('Flexible height'))),
            ('max_width', models.PositiveIntegerField(_('Max width'))),
            ('resample_quality', models.IntegerField(_('Resample quality'), default=85)),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('photos', ['Format'])
        
        # Adding ManyToManyField 'Photo.authors'
        db.create_table('photos_photo_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('photo', models.ForeignKey(Photo, null=False)),
            ('author', models.ForeignKey(Author, null=False))
        ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Photo'
        db.delete_table('photos_photo')
        
        # Deleting model 'FormatedPhoto'
        db.delete_table('photos_formatedphoto')
        
        # Deleting model 'Format'
        db.delete_table('photos_format')
        
        # Dropping ManyToManyField 'Photo.authors'
        db.delete_table('photos_photo_authors')
        
    
    
    models = {
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'db_table': "'django_site'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.source': {
            'Meta': {'ordering': "('name',)", 'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.author': {
            'Meta': {'ordering': "('name','slug',)", 'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'photos.photo': {
            'Meta': {'ordering': "('-created',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'photos.format': {
            'Meta': {'ordering': "('name','-max_width',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    
