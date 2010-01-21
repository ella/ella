
from south.db import db
from django.db import models
from ella.media.models import *
import datetime

class Migration:
    
    depends_on = (
        ("core", "0001_initial"),
        ("photos", "0001_initial"),
    )
 
    def forwards(self, orm):
        
        # Adding model 'Usage'
        db.create_table('media_usage', (
            ('id', models.AutoField(primary_key=True)),
            ('media', models.ForeignKey(orm.Media)),
            ('title', models.CharField(_('Title'), max_length=255)),
            ('url', models.URLField(_('Url'), max_length=255)),
            ('priority', models.SmallIntegerField(_('Priority'))),
        ))
        db.send_create_signal('media', ['Usage'])
        
        # Adding model 'Media'
        db.create_table('media_media', (
            ('id', models.AutoField(primary_key=True)),
            ('title', models.CharField(_('Title'), max_length=255)),
            ('slug', models.SlugField(_('Slug'), max_length=255)),
            ('photo', models.ForeignKey(orm['photos.Photo'], null=True, verbose_name=_('Preview image'), blank=True)),
            ('file', MediaField()),
            ('source', models.ForeignKey(orm['core.Source'], null=True, verbose_name=_('Source'), blank=True)),
            ('category', models.ForeignKey(orm['core.Category'], null=True, verbose_name=_('Category'))),
            ('description', models.TextField(_('Description'), blank=True)),
            ('text', models.TextField(_('Content'), blank=True)),
            ('created', models.DateTimeField(_('Created'), default=datetime.datetime.now, editable=False)),
            ('updated', models.DateTimeField(_('Updated'), null=True, blank=True)),
        ))
        db.send_create_signal('media', ['Media'])
        
        # Adding model 'Section'
        db.create_table('media_section', (
            ('id', models.AutoField(primary_key=True)),
            ('media', models.ForeignKey(orm.Media)),
            ('title', models.CharField(_('Title'), max_length=255)),
            ('description', models.TextField(_('Description'), blank=True)),
            ('time', MediaTimeField(_('Start time in miliseconds'))),
            ('duration', MediaTimeField(_('Duration in miliseconds'), null=True, blank=True)),
        ))
        db.send_create_signal('media', ['Section'])
        
        # Adding ManyToManyField 'Media.authors'
        db.create_table('media_media_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('media', models.ForeignKey(orm.Media, null=False)),
            ('author', models.ForeignKey(orm['core.Author'], null=False))
        ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Usage'
        db.delete_table('media_usage')
        
        # Deleting model 'Media'
        db.delete_table('media_media')
        
        # Deleting model 'Section'
        db.delete_table('media_section')
        
        # Dropping ManyToManyField 'Media.authors'
        db.delete_table('media_media_authors')
        
    
    
    models = {
        'core.category': {
            'Meta': {'ordering': "('site','tree_path',)", 'unique_together': "(('site','tree_path'),)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'media.media': {
            'authors': ('models.ManyToManyField', ["orm['core.Author']"], {'verbose_name': "_('Authors')"}),
            'category': ('models.ForeignKey', ["orm['core.Category']"], {'null': 'True', 'verbose_name': "_('Category')"}),
            'created': ('models.DateTimeField', ["_('Created')"], {'default': 'datetime.datetime.now', 'editable': 'False'}),
            'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
            'file': ('MediaField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'photo': ('models.ForeignKey', ["orm['photos.Photo']"], {'null': 'True', 'verbose_name': "_('Preview image')", 'blank': 'True'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'source': ('models.ForeignKey', ["orm['core.Source']"], {'null': 'True', 'verbose_name': "_('Source')", 'blank': 'True'}),
            'text': ('models.TextField', ["_('Content')"], {'blank': 'True'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '255'}),
            'updated': ('models.DateTimeField', ["_('Updated')"], {'null': 'True', 'blank': 'True'})
        },
        'media.usage': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'media': ('models.ForeignKey', ["orm['media.Media']"], {}),
            'priority': ('models.SmallIntegerField', ["_('Priority')"], {}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '255'}),
            'url': ('models.URLField', ["_('Url')"], {'max_length': '255'})
        },
        'photos.photo': {
            'Meta': {'ordering': "('-created',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'media.section': {
            'Meta': {'ordering': "('id',)"},
            'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
            'duration': ('MediaTimeField', ["_('Duration in miliseconds')"], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'media': ('models.ForeignKey', ["orm['media.Media']"], {}),
            'time': ('MediaTimeField', ["_('Start time in miliseconds')"], {}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '255'})
        },
        'cdnclient.source': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
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
    
    complete_apps = ['media']
