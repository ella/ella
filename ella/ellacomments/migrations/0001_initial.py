
from south.db import db
from django.db import models
from ella.ellacomments.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'CommentOptionsObject'
        db.create_table('ellacomments_commentoptionsobject', (
            ('id', models.AutoField(primary_key=True)),
            ('target_ct', models.ForeignKey(orm['contenttypes.ContentType'], verbose_name=_('Target content type'))),
            ('target_id', models.PositiveIntegerField(_('Target id'))),
            ('blocked', models.BooleanField(_('Disable comments'), default=False)),
            ('premoderated', models.BooleanField(_('Show comments only after approval'), default=False)),
            ('check_profanities', models.BooleanField(_('Check profanities in comments'), default=False, editable=False)),
        ))
        db.send_create_signal('ellacomments', ['CommentOptionsObject'])
        
        # Creating unique_together for [target_ct, target_id] on CommentOptionsObject.
        db.create_unique('ellacomments_commentoptionsobject', ['target_ct_id', 'target_id'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'CommentOptionsObject'
        db.delete_table('ellacomments_commentoptionsobject')
        
        # Deleting unique_together for [target_ct, target_id] on CommentOptionsObject.
        db.delete_unique('ellacomments_commentoptionsobject', ['target_ct_id', 'target_id'])
        
    
    
    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'ellacomments.commentoptionsobject': {
            'Meta': {'unique_together': "(('target_ct','target_id',),)"},
            'blocked': ('models.BooleanField', ["_('Disable comments')"], {'default': 'False'}),
            'check_profanities': ('models.BooleanField', ["_('Check profanities in comments')"], {'default': 'False', 'editable': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'premoderated': ('models.BooleanField', ["_('Show comments only after approval')"], {'default': 'False'}),
            'target_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'verbose_name': "_('Target content type')"}),
            'target_id': ('models.PositiveIntegerField', ["_('Target id')"], {})
        }
    }
    
    complete_apps = ['ellacomments']
