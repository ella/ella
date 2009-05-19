
from south.db import db
from django.db import models
from ella.positions.models import *

class Migration:
    
    depends_on = (
        ("core", "0001_initial"),
    )
 
    def forwards(self, orm):
        
        # Adding model 'Position'
        db.create_table('positions_position', (
            ('id', models.AutoField(primary_key=True)),
            ('category', models.ForeignKey(orm['core.Category'], verbose_name=_('Category'))),
            ('name', models.CharField(_('Name'), max_length=200)),
            ('target_ct', models.ForeignKey(orm['contenttypes.ContentType'], null=True, verbose_name=_('Target content type'), blank=True)),
            ('target_id', models.PositiveIntegerField(_('Target id'), null=True, blank=True)),
            ('active_from', models.DateTimeField(_('Position active from'), null=True, blank=True)),
            ('active_till', models.DateTimeField(_('Position active till'), null=True, blank=True)),
            ('box_type', models.CharField(_('Box type'), max_length=200, blank=True)),
            ('text', models.TextField(_('Definition'), blank=True)),
            ('disabled', models.BooleanField(_('Disabled'), default=False)),
        ))
        db.send_create_signal('positions', ['Position'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Position'
        db.delete_table('positions_position')
        
    
    
    models = {
        'core.category': {
            'Meta': {'ordering': "('site','tree_path',)", 'unique_together': "(('site','tree_path'),)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'positions.position': {
            'active_from': ('models.DateTimeField', ["_('Position active from')"], {'null': 'True', 'blank': 'True'}),
            'active_till': ('models.DateTimeField', ["_('Position active till')"], {'null': 'True', 'blank': 'True'}),
            'box_type': ('models.CharField', ["_('Box type')"], {'max_length': '200', 'blank': 'True'}),
            'category': ('models.ForeignKey', ["orm['core.Category']"], {'verbose_name': "_('Category')"}),
            'disabled': ('models.BooleanField', ["_('Disabled')"], {'default': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ["_('Name')"], {'max_length': '200'}),
            'target_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'null': 'True', 'verbose_name': "_('Target content type')", 'blank': 'True'}),
            'target_id': ('models.PositiveIntegerField', ["_('Target id')"], {'null': 'True', 'blank': 'True'}),
            'text': ('models.TextField', ["_('Definition')"], {'blank': 'True'})
        }
    }
    
    complete_apps = ['positions']
