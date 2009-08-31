
from south.db import db
from django.db import models
from ella.newman.licenses.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'License'
        db.create_table('licenses_license', (
            ('id', models.AutoField(primary_key=True)),
            ('ct', models.ForeignKey(orm['contenttypes.ContentType'])),
            ('obj_id', models.PositiveIntegerField(_('Object ID'))),
            ('max_applications', models.PositiveIntegerField(_('Max applications'))),
            ('applications', models.PositiveIntegerField(default=0, editable=False)),
            ('note', models.CharField(_('Note'), max_length=255, blank=True)),
        ))
        db.send_create_signal('licenses', ['License'])
        
        # Creating unique_together for [ct, obj_id] on License.
        db.create_unique('licenses_license', ['ct_id', 'obj_id'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'License'
        db.delete_table('licenses_license')
        
        # Deleting unique_together for [ct, obj_id] on License.
        db.delete_unique('licenses_license', ['ct_id', 'obj_id'])
        
    
    
    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'licenses.license': {
            'Meta': {'unique_together': "(('ct','obj_id',),)"},
            'applications': ('models.PositiveIntegerField', [], {'default': '0', 'editable': 'False'}),
            'ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'max_applications': ('models.PositiveIntegerField', ["_('Max applications')"], {}),
            'note': ('models.CharField', ["_('Note')"], {'max_length': '255', 'blank': 'True'}),
            'obj_id': ('models.PositiveIntegerField', ["_('Object ID')"], {})
        }
    }
    
    complete_apps = ['licenses']
