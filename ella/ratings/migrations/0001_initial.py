
from south.db import db
from django.db import models
from ella.ratings.models import *
import datetime

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Agg'
        db.create_table('ratings_agg', (
            ('id', models.AutoField(primary_key=True)),
            ('target_ct', models.ForeignKey(orm['contenttypes.ContentType'], db_index=True)),
            ('target_id', models.PositiveIntegerField(_('Object ID'), db_index=True)),
            ('time', models.DateField(_('Time'))),
            ('people', models.IntegerField(_('People'))),
            ('amount', models.DecimalField(_('Amount'), max_digits=10, decimal_places=2)),
            ('period', models.CharField(_('Period'), max_length="1")),
            ('detract', models.IntegerField(_('Detract'), default=0, max_length=1)),
        ))
        db.send_create_signal('ratings', ['Agg'])
        
        # Adding model 'ModelWeight'
        db.create_table('ratings_modelweight', (
            ('id', models.AutoField(primary_key=True)),
            ('content_type', models.OneToOneField(orm['contenttypes.ContentType'])),
            ('weight', models.IntegerField(_('Weight'), default=1)),
            ('owner_field', models.CharField(_('Owner field'), max_length=30)),
        ))
        db.send_create_signal('ratings', ['ModelWeight'])
        
        # Adding model 'TotalRate'
        db.create_table('ratings_totalrate', (
            ('id', models.AutoField(primary_key=True)),
            ('target_ct', models.ForeignKey(orm['contenttypes.ContentType'], db_index=True)),
            ('target_id', models.PositiveIntegerField(_('Object ID'), db_index=True)),
            ('amount', models.DecimalField(_('Amount'), max_digits=10, decimal_places=2)),
        ))
        db.send_create_signal('ratings', ['TotalRate'])
        
        # Adding model 'Rating'
        db.create_table('ratings_rating', (
            ('id', models.AutoField(primary_key=True)),
            ('target_ct', models.ForeignKey(orm['contenttypes.ContentType'], db_index=True)),
            ('target_id', models.PositiveIntegerField(_('Object ID'), db_index=True)),
            ('time', models.DateTimeField(_('Time'), default=datetime.datetime.now, editable=False)),
            ('user', models.ForeignKey(orm['auth.User'], null=True, blank=True)),
            ('amount', models.DecimalField(_('Amount'), max_digits=10, decimal_places=2)),
            ('ip_address', models.CharField(_('IP Address'), max_length="15", blank=True)),
        ))
        db.send_create_signal('ratings', ['Rating'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Agg'
        db.delete_table('ratings_agg')
        
        # Deleting model 'ModelWeight'
        db.delete_table('ratings_modelweight')
        
        # Deleting model 'TotalRate'
        db.delete_table('ratings_totalrate')
        
        # Deleting model 'Rating'
        db.delete_table('ratings_rating')
        
    
    
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
            'time': ('models.DateTimeField', ["_('Time')"], {'default': 'datetime.datetime.now', 'editable': 'False'}),
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
