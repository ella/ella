
from south.db import db
from django.db import models
from ella.db_templates.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'TemplateBlock'
        db.create_table('db_templates_templateblock', (
            ('id', models.AutoField(primary_key=True)),
            ('template', models.ForeignKey(orm.DbTemplate)),
            ('name', models.CharField(_('Name'), max_length=200)),
            ('box_type', models.CharField(_('Box type'), max_length=200, blank=True)),
            ('target_ct', models.ForeignKey(orm['contenttypes.ContentType'], null=True, blank=True)),
            ('target_id', models.IntegerField(null=True, blank=True)),
            ('active_from', models.DateTimeField(_('Block active from'), null=True, blank=True)),
            ('active_till', models.DateTimeField(_('Block active till'), null=True, blank=True)),
            ('text', models.TextField(_('Definition'), blank=True)),
        ))
        db.send_create_signal('db_templates', ['TemplateBlock'])
        
        # Adding model 'DbTemplate'
        db.create_table('db_templates_dbtemplate', (
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(_('Name'), max_length=200, db_index=True)),
            ('site', models.ForeignKey(orm['sites.Site'])),
            ('description', models.CharField(_('Description'), max_length=500, blank=True)),
            ('extends', models.CharField(_('Base template'), max_length=200)),
        ))
        db.send_create_signal('db_templates', ['DbTemplate'])
        
        # Creating unique_together for [template, name, active_from, active_till] on TemplateBlock.
        db.create_unique('db_templates_templateblock', ['template_id', 'name', 'active_from', 'active_till'])
        
        # Creating unique_together for [site, name] on DbTemplate.
        db.create_unique('db_templates_dbtemplate', ['site_id', 'name'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'TemplateBlock'
        db.delete_table('db_templates_templateblock')
        
        # Deleting model 'DbTemplate'
        db.delete_table('db_templates_dbtemplate')
        
        # Deleting unique_together for [template, name, active_from, active_till] on TemplateBlock.
        db.delete_unique('db_templates_templateblock', ['template_id', 'name', 'active_from', 'active_till'])
        
        # Deleting unique_together for [site, name] on DbTemplate.
        db.delete_unique('db_templates_dbtemplate', ['site_id', 'name'])
        
    
    
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
