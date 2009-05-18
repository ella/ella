
from south.db import db
from django.db import models
from ella.core.models import *

class Migration:
    
    def forwards(self, orm):
        "Write your forwards migration here"
    
    
    def backwards(self, orm):
        "Write your backwards migration here"
    
    
    models = {
        'core.placement': {
            'Meta': {'ordering': "('-publish_from',)"},
            'category': ('models.ForeignKey', ["orm['core.Category']"], {'db_index': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'publish_from': ('models.DateTimeField', ['_("Start of visibility")'], {}),
            'publish_to': ('models.DateTimeField', ['_("End of visibility")'], {'null': 'True', 'blank': 'True'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255', 'blank': 'True'}),
            'static': ('models.BooleanField', [], {'default': 'False'}),
            'target_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {}),
            'target_id': ('models.IntegerField', [], {})
        },
        'core.category': {
            'Meta': {'ordering': "('site','tree_path',)", 'unique_together': "(('site','tree_path'),)"},
            'description': ('models.TextField', ['_("Category Description")'], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'site': ('models.ForeignKey', ["orm['sites.Site']"], {}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'title': ('models.CharField', ['_("Category Title")'], {'max_length': '200'}),
            'tree_parent': ('models.ForeignKey', ["orm['core.Category']"], {'null': 'True', 'verbose_name': '_("Parent Category")', 'blank': 'True'}),
            'tree_path': ('models.CharField', [], {'editable': 'False', 'max_length': '255', 'verbose_name': '_("Path from root category")'})
        },
        'core.listing': {
            'Meta': {'ordering': "('-publish_from',)"},
            'category': ('models.ForeignKey', ["orm['core.Category']"], {'db_index': 'True'}),
            'commercial': ('models.BooleanField', ['_("Commercial")'], {'default': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'placement': ('models.ForeignKey', ["orm['core.Placement']"], {}),
            'priority_from': ('models.DateTimeField', ['_("Start of prioritized listing")'], {'null': 'True', 'blank': 'True'}),
            'priority_to': ('models.DateTimeField', ['_("End of prioritized listing")'], {'null': 'True', 'blank': 'True'}),
            'priority_value': ('models.IntegerField', ['_("Priority")'], {'null': 'True', 'blank': 'True'}),
            'publish_from': ('models.DateTimeField', ['_("Start of listing")'], {}),
            'remove': ('models.BooleanField', ['_("Remove")'], {'default': 'False'})
        },
        'core.hitcount': {
            'hits': ('models.PositiveIntegerField', ["_('Hits')"], {'default': '1'}),
            'last_seen': ('models.DateTimeField', ["_('Last seen')"], {'editable': 'False'}),
            'placement': ('models.ForeignKey', ["orm['core.Placement']"], {'primary_key': 'True'})
        },
        'core.related': {
            'Meta': {'ordering': "('source_ct','source_id',)"},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'source_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'related_name': "'related_on_set'"}),
            'source_id': ('models.IntegerField', [], {}),
            'target_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'related_name': "'relation_for_set'"}),
            'target_id': ('models.IntegerField', [], {})
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
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.source': {
            'Meta': {'ordering': "('name',)"},
            'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ["_('Name')"], {'max_length': '200'}),
            'url': ('models.URLField', ["_('URL')"], {'blank': 'True'})
        },
        'core.author': {
            'Meta': {'ordering': "('name','slug',)"},
            'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ["_('Name')"], {'max_length': '200', 'blank': 'True'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'unique': 'True', 'max_length': '255'}),
            'text': ('models.TextField', ["_('Text')"], {'blank': 'True'}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'null': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['core']
