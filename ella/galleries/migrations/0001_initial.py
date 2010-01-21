
from south.db import db
from django.db import models
from ella.galleries.models import *
import datetime

class Migration:
    
    depends_on = (
        ("core", "0001_initial"),
        ("photos", "0001_initial"),
    )
 
    def forwards(self, orm):
        
        # Adding model 'GalleryItem'
        db.create_table('galleries_galleryitem', (
            ('id', models.AutoField(primary_key=True)),
            ('gallery', models.ForeignKey(orm.Gallery, verbose_name=_("Parent gallery"))),
            ('target_ct', models.ForeignKey(orm['contenttypes.ContentType'], verbose_name=_('Target content type'))),
            ('target_id', models.IntegerField(_('Target ID'), db_index=True)),
            ('order', models.IntegerField(_('Object order'))),
        ))
        db.send_create_signal('galleries', ['GalleryItem'])
        
        # Adding model 'Gallery'
        db.create_table('galleries_gallery', (
            ('id', models.AutoField(primary_key=True)),
            ('title', models.CharField(_('Title'), max_length=255)),
            ('slug', models.SlugField(_('Slug'), max_length=255)),
            ('description', models.CharField(_('Description'), max_length=3000, blank=True)),
            ('content', models.TextField(_('Content'), blank=True)),
            ('owner', models.ForeignKey(orm['core.Author'], null=True, verbose_name=_('Gallery owner'), blank=True)),
            ('category', models.ForeignKey(orm['core.Category'], null=True, verbose_name=_('Category'), blank=True)),
            ('created', models.DateTimeField(_('Created'), default=datetime.datetime.now, editable=False)),
        ))
        db.send_create_signal('galleries', ['Gallery'])
        
        # Creating unique_together for [gallery, order] on GalleryItem.
        db.create_unique('galleries_galleryitem', ['gallery_id', 'order'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'GalleryItem'
        db.delete_table('galleries_galleryitem')
        
        # Deleting model 'Gallery'
        db.delete_table('galleries_gallery')
        
        # Deleting unique_together for [gallery, order] on GalleryItem.
        db.delete_unique('galleries_galleryitem', ['gallery_id', 'order'])
        
    
    
    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
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
            'created': ('models.DateTimeField', ["_('Created')"], {'default': 'datetime.datetime.now', 'editable': 'False'}),
            'description': ('models.CharField', ["_('Description')"], {'max_length': '3000', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'owner': ('models.ForeignKey', ["orm['core.Author']"], {'null': 'True', 'verbose_name': "_('Gallery owner')", 'blank': 'True'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '255'})
        },
        'core.author': {
            'Meta': {'ordering': "('name','slug',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    complete_apps = ['galleries']
