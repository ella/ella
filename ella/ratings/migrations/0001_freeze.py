
from south.db import db
from django.db import models
from ella.ratings.models import *

class Migration:
    
    def forwards(self, orm):
        "Write your forwards migration here"
    
    
    def backwards(self, orm):
        "Write your backwards migration here"
    
    
    models = {
        'ratings.agg': {
            'Meta': {'ordering': "('-time',)"},
            'amount': ('models.DecimalField', ["_('Amount')"], {'max_digits': '10', 'decimal_places': '2'}),
            'detract': ('models.IntegerField', ["_('Detract')"], {'default': '0', 'max_length': '1'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'people': ('models.IntegerField', ["_('People')"], {}),
            'period': ('models.CharField', ["_('Period')"], {'max_length': '"1"'}),
            'target_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'db_index': 'True'}),
            'target_id': ('models.PositiveIntegerField', ["_('Object ID')"], {'db_index': 'True'}),
            'time': ('models.DateField', ["_('Time')"], {})
        },
        'ratings.rating': {
            'Meta': {'ordering': "('-time',)"},
            'amount': ('models.DecimalField', ["_('Amount')"], {'max_digits': '10', 'decimal_places': '2'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('models.CharField', ["_('IP Address')"], {'max_length': '"15"', 'blank': 'True'}),
            'target_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'db_index': 'True'}),
            'target_id': ('models.PositiveIntegerField', ["_('Object ID')"], {'db_index': 'True'}),
            'time': ('models.DateTimeField', ["_('Time')"], {'default': 'datetime.now', 'editable': 'False'}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'null': 'True', 'blank': 'True'})
        },
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'ratings.totalrate': {
            'amount': ('models.DecimalField', ["_('Amount')"], {'max_digits': '10', 'decimal_places': '2'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'target_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'db_index': 'True'}),
            'target_id': ('models.PositiveIntegerField', ["_('Object ID')"], {'db_index': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'ratings.modelweight': {
            'Meta': {'ordering': "('-weight',)"},
            'content_type': ('models.OneToOneField', ["orm['contenttypes.ContentType']"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'owner_field': ('models.CharField', ["_('Owner field')"], {'max_length': '30'}),
            'weight': ('models.IntegerField', ["_('Weight')"], {'default': '1'})
        }
    }
    
    complete_apps = ['ratings']
