
from south.db import db
from django.db import models
from ella.comments.models import *

class Migration:
    
    def forwards(self, orm):
        "Write your forwards migration here"
    
    
    def backwards(self, orm):
        "Write your backwards migration here"
    
    
    models = {
        'comments.bannedip': {
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'comments.comment': {
            'Meta': {'ordering': "('-path',)"},
            'content': ('models.TextField', ["_('Comment content')"], {'max_length': 'defaults.COMMENT_LENGTH'}),
            'email': ('models.EmailField', ["_('Authors email (optional)')"], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('models.IPAddressField', ["_('IP address')"], {'null': 'True', 'blank': 'True'}),
            'is_public': ('models.BooleanField', ["_('Is public')"], {'default': 'True'}),
            'nickname': ('models.CharField', ['_("Anonymous author\'s nickname")'], {'max_length': 'defaults.NICKNAME_LENGTH', 'blank': 'True'}),
            'parent': ('models.ForeignKey', ["orm['comments.Comment']"], {'null': 'True', 'verbose_name': "_('Tree structure parent')", 'blank': 'True'}),
            'path': ('models.CharField', ["_('Genealogy tree path')"], {'max_length': 'defaults.PATH_LENGTH', 'editable': 'False', 'blank': 'True'}),
            'subject': ('models.TextField', ["_('Comment subject')"], {'max_length': 'defaults.SUBJECT_LENGTH'}),
            'submit_date': ('models.DateTimeField', ["_('Time submitted')"], {'default': 'datetime.now', 'editable': 'True'}),
            'target_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'verbose_name': "_('Target content type')"}),
            'target_id': ('models.PositiveIntegerField', ["_('Target id')"], {}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'null': 'True', 'verbose_name': "_('Authorized author')", 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'comments.commentoptions': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'options': ('models.CharField', [], {'max_length': 'defaults.OPTS_LENGTH', 'blank': 'True'}),
            'target_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'verbose_name': "_('Target content type')"}),
            'target_id': ('models.PositiveIntegerField', ["_('Target id')"], {}),
            'timestamp': ('models.DateTimeField', [], {'default': 'datetime.now'})
        },
        'comments.banneduser': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'target_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'verbose_name': "_('Target content type')"}),
            'target_id': ('models.PositiveIntegerField', ["_('Target id')"], {}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'verbose_name': "_('Banned author')"})
        }
    }
    
    complete_apps = ['comments']
