
from south.db import db
from django.db import models
from ella.oldcomments.models import *
import datetime

class Migration:
    
    def forwards(self, orm):
        "Write your forwards migration here"
        db.add_column('django_comments', 'old_id', models.IntegerField(null=True, db_index=True))
    
    
    def backwards(self, orm):
        "Write your backwards migration here"
        db.delete_column('django_comments', 'old_id')
    
    
    models = {
        'oldcomments.comment': {
            'Meta': {'ordering': "('-path',)", 'db_table': "'comments_comment'"},
            'content': ('models.TextField', ["_('Comment content')"], {'max_length': 'defaults.COMMENT_LENGTH'}),
            'email': ('models.EmailField', ["_('Authors email (optional)')"], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('models.IPAddressField', ["_('IP address')"], {'null': 'True', 'blank': 'True'}),
            'is_public': ('models.BooleanField', ["_('Is public')"], {'default': 'True'}),
            'nickname': ('models.CharField', ['_("Anonymous author\'s nickname")'], {'max_length': 'defaults.NICKNAME_LENGTH', 'blank': 'True'}),
            'parent': ('models.ForeignKey', ["orm['oldcomments.Comment']"], {'null': 'True', 'verbose_name': "_('Tree structure parent')", 'blank': 'True'}),
            'path': ('models.CharField', ["_('Genealogy tree path')"], {'max_length': 'defaults.PATH_LENGTH', 'editable': 'False', 'blank': 'True'}),
            'subject': ('models.TextField', ["_('Comment subject')"], {'max_length': 'defaults.SUBJECT_LENGTH'}),
            'submit_date': ('models.DateTimeField', ["_('Time submitted')"], {'default': 'datetime.datetime.now', 'editable': 'True'}),
            'target_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'verbose_name': "_('Target content type')"}),
            'target_id': ('models.PositiveIntegerField', ["_('Target id')"], {}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'null': 'True', 'verbose_name': "_('Authorized author')", 'blank': 'True'})
        },
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'oldcomments.banneduser': {
            'Meta': {'db_table': "'comments_banneduser'"},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'target_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'verbose_name': "_('Target content type')"}),
            'target_id': ('models.PositiveIntegerField', ["_('Target id')"], {}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'verbose_name': "_('Banned author')"})
        },
        'oldcomments.bannedip': {
            'Meta': {'db_table': "'comments_bannedip'"},
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'oldcomments.commentoptions': {
            'Meta': {'db_table': "'comments_commentoptions'"},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'options': ('models.CharField', [], {'max_length': 'defaults.OPTS_LENGTH', 'blank': 'True'}),
            'target_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'verbose_name': "_('Target content type')"}),
            'target_id': ('models.PositiveIntegerField', ["_('Target id')"], {}),
            'timestamp': ('models.DateTimeField', [], {'default': 'datetime.datetime.now'})
        }
    }
    
    complete_apps = ['oldcomments']
