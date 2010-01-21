
from south.db import db
from django.db import models
from ella.sendmail.models import *
import datetime

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Mail'
        db.create_table('sendmail_mail', (
            ('id', models.AutoField(primary_key=True)),
            ('sender', models.EmailField()),
            ('recipient', models.EmailField()),
            ('sent', models.DateTimeField(default=datetime.datetime.now)),
            ('target_ct', models.ForeignKey(orm['contenttypes.ContentType'], verbose_name=_('content type'))),
            ('target_id', models.PositiveIntegerField(_('target id'), db_index=True)),
            ('content', models.TextField(null=True, blank=True)),
        ))
        db.send_create_signal('sendmail', ['Mail'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Mail'
        db.delete_table('sendmail_mail')
        
    
    
    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'sendmail.mail': {
            'content': ('models.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'recipient': ('models.EmailField', [], {}),
            'sender': ('models.EmailField', [], {}),
            'sent': ('models.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'target_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'verbose_name': "_('content type')"}),
            'target_id': ('models.PositiveIntegerField', ["_('target id')"], {'db_index': 'True'})
        }
    }
    
    complete_apps = ['sendmail']
