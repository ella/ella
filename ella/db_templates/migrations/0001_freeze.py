
from south.db import db
from django.db import models
from ella.db_templates.models import *

class Migration:
    
    def forwards(self, orm):
        "Write your forwards migration here"
    
    
    def backwards(self, orm):
        "Write your backwards migration here"
    
    
    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'db_table': "'django_site'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'db_templates.templateblock': {
            'Meta': {'unique_together': "(('template','name','active_from','active_till',),)"},
            'active_from': ('models.DateTimeField', ["_('Block active from')"], {'null': 'True', 'blank': 'True'}),
            'active_till': ('models.DateTimeField', ["_('Block active till')"], {'null': 'True', 'blank': 'True'}),
            'box_type': ('models.CharField', ["_('Box type')"], {'max_length': '200', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ["_('Name')"], {'max_length': '200'}),
            'target_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'null': 'True', 'blank': 'True'}),
            'target_id': ('models.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'template': ('models.ForeignKey', ["orm['db_templates.DbTemplate']"], {}),
            'text': ('models.TextField', ["_('Definition')"], {'blank': 'True'})
        },
        'db_templates.dbtemplate': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('site','name'),)"},
            'description': ('models.CharField', ["_('Description')"], {'max_length': '500', 'blank': 'True'}),
            'extends': ('models.CharField', ["_('Base template')"], {'max_length': '200'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ["_('Name')"], {'max_length': '200', 'db_index': 'True'}),
            'site': ('models.ForeignKey', ["orm['sites.Site']"], {})
        }
    }
    
    complete_apps = ['db_templates']
