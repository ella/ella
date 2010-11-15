from south.db import db
from django.db import models
from ella.core.models import *
import datetime
from south.v2 import SchemaMigration

class Migration(SchemaMigration):

    def forwards(self, orm):
        "Write your forwards migration here"
        db.create_index('core_listing', ['publish_from'])


    def backwards(self, orm):
        "Write your backwards migration here"


    models = {
        'core.placement': {
            'Meta': {'unique_together': "(('publishable','category',),)", 'app_label': "'core'"},
            'category': ('models.ForeignKey', ["orm['core.Category']"], {'verbose_name': "_('Category')", 'db_index': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'publish_from': ('models.DateTimeField', ['_("Start of visibility")'], {}),
            'publish_to': ('models.DateTimeField', ['_("End of visibility")'], {'null': 'True', 'blank': 'True'}),
            'publishable': ('models.ForeignKey', ["orm['core.Publishable']"], {'verbose_name': "_('Publishable object')"}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255', 'blank': 'True'}),
            'static': ('models.BooleanField', ["_('static')"], {'default': 'False'})
        },
        'core.category': {
            'Meta': {'unique_together': "(('site','tree_path'),)", 'app_label': "'core'"},
            'description': ('models.TextField', ['_("Category Description")'], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'site': ('models.ForeignKey', ["orm['sites.Site']"], {}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'title': ('models.CharField', ['_("Category Title")'], {'max_length': '200'}),
            'tree_parent': ('models.ForeignKey', ["orm['core.Category']"], {'null': 'True', 'verbose_name': '_("Parent Category")', 'blank': 'True'}),
            'tree_path': ('models.CharField', [], {'editable': 'False', 'max_length': '255', 'verbose_name': '_("Path from root category")'})
        },
        'core.listing': {
            'Meta': {'ordering': "('-publish_from',)", 'app_label': "'core'"},
            'category': ('models.ForeignKey', ["orm['core.Category']"], {'verbose_name': "_('Category')", 'db_index': 'True'}),
            'commercial': ('models.BooleanField', ['_("Commercial")'], {'default': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'placement': ('models.ForeignKey', ["orm['core.Placement']"], {'verbose_name': "_('Placement')"}),
            'priority_from': ('models.DateTimeField', ['_("Start of prioritized listing")'], {'null': 'True', 'blank': 'True'}),
            'priority_to': ('models.DateTimeField', ['_("End of prioritized listing")'], {'null': 'True', 'blank': 'True'}),
            'priority_value': ('models.IntegerField', ['_("Priority")'], {'null': 'True', 'blank': 'True'}),
            'publish_from': ('models.DateTimeField', ['_("Start of listing")'], {'db_index': 'True'}),
            'publish_to': ('models.DateTimeField', ['_("End of listing")'], {'null': 'True', 'blank': 'True'})
        },
        'core.hitcount': {
            'Meta': {'app_label': "'core'"},
            'hits': ('models.PositiveIntegerField', ["_('Hits')"], {'default': '1'}),
            'last_seen': ('models.DateTimeField', ["_('Last seen')"], {'editable': 'False'}),
            'placement': ('models.ForeignKey', ["orm['core.Placement']"], {'primary_key': 'True'})
        },
        'core.related': {
            'Meta': {'app_label': "'core'"},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'publishable': ('models.ForeignKey', ["orm['core.Publishable']"], {'verbose_name': "_('Publishable')"}),
            'related_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'verbose_name': "_('Content type')"}),
            'related_id': ('models.IntegerField', ["_('Object ID')"], {})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'db_table': "'django_site'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'photos.photo': {
            'Meta': {'ordering': "('-created',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.publishable': {
            'Meta': {'app_label': "'core'"},
            'authors': ('models.ManyToManyField', ["orm['core.Author']"], {'verbose_name': "_('Authors')"}),
            'category': ('models.ForeignKey', ["orm['core.Category']"], {'verbose_name': "_('Category')"}),
            'content_type': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {}),
            'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'photo': ('models.ForeignKey', ["orm['photos.Photo']"], {'null': 'True', 'verbose_name': "_('Photo')", 'blank': 'True'}),
            'publish_from': ('models.DateTimeField', ["_('Publish from')"], {'default': 'datetime.datetime(3000, 1, 1, 0, 0)', 'editable': 'False', 'db_index': 'True'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'source': ('models.ForeignKey', ["orm['core.Source']"], {'null': 'True', 'verbose_name': "_('Source')", 'blank': 'True'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '255'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.source': {
            'Meta': {'app_label': "'core'"},
            'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ["_('Name')"], {'max_length': '200'}),
            'url': ('models.URLField', ["_('URL')"], {'blank': 'True'})
        },
        'core.dependency': {
            'Meta': {'ordering': "('dependent_ct','dependent_id',)", 'app_label': "'core'"},
            'dependent_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'related_name': "'depends_on_set'"}),
            'dependent_id': ('models.IntegerField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'target_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'related_name': "'dependency_for_set'"}),
            'target_id': ('models.IntegerField', [], {})
        },
        'core.author': {
            'Meta': {'app_label': "'core'"},
            'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
            'email': ('models.EmailField', ["_('Email')"], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ["_('Name')"], {'max_length': '200', 'blank': 'True'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'unique': 'True', 'max_length': '255'}),
            'text': ('models.TextField', ["_('Text')"], {'blank': 'True'}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'null': 'True', 'verbose_name': "_('User')", 'blank': 'True'})
        }
    }

    complete_apps = ['core']
