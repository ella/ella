
from south.db import db
from django.db import models
from ella.tagging.models import *

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
        'tagging.taggeditem': {
            'Meta': {'unique_together': "(('tag','content_type','object_id','priority'),)"},
            'category': ('models.ForeignKey', ["orm['core.Category']"], {'null': 'True', 'editable': 'False'}),
            'content_type': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'verbose_name': "_('content type')"}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('models.PositiveIntegerField', ["_('object id')"], {'db_index': 'True'}),
            'priority': ('models.IntegerField', [], {'db_index': 'True'}),
            'tag': ('models.ForeignKey', ["orm['tagging.Tag']"], {'related_name': "'items'", 'verbose_name': "_('tag')"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'tagging.tag': {
            'Meta': {'ordering': "('name',)"},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ["_('name')"], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
        }
    }
    
    complete_apps = ['tagging']
