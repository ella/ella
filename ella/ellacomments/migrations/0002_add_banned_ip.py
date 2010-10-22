import datetime
from south.db import db
from django.db import models
from ella.ellacomments.models import *

class Migration:

    def forwards(self, orm):

        # Adding model 'BannedIP'
        db.create_table('ellacomments_bannedip', (
            ('id', models.AutoField(primary_key=True)),
            ('created', models.DateTimeField(_('Created'), default=datetime.datetime.now, editable=False)),
            ('ip_address', models.IPAddressField(_('IP Address'), unique=True)),
            ('reason', models.CharField(_('Reason'), max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('ellacomments', ['BannedIP'])



    def backwards(self, orm):

        # Deleting model 'BannedIP'
        db.delete_table('ellacomments_bannedip')



    models = {
        'ellacomments.bannedip': {
            'Meta': {'ordering': "('-created',)"},
            'created': ('models.DateTimeField', ["_('Created')"], {'default': 'datetime.datetime.now', 'editable': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('models.IPAddressField', ["_('IP Address')"], {'unique': 'True'}),
            'reason': ('models.CharField', ["_('Reason')"], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
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
