
from south.db import db
from django.db import models
from ella.oldcomments.models import *
import datetime

class Migration:

    def forwards(self, orm):

        # Adding model 'BannedUser'
        db.create_table('comments_banneduser', (
            ('id', models.AutoField(primary_key=True)),
            ('target_ct', models.ForeignKey(orm['contenttypes.ContentType'], verbose_name=_('Target content type'))),
            ('target_id', models.PositiveIntegerField(_('Target id'))),
            ('user', models.ForeignKey(orm['auth.User'], verbose_name=_('Banned author'))),
        ))
        db.send_create_signal('comments', ['BannedUser'])

        # Adding model 'Comment'
        db.create_table('comments_comment', (
            ('id', models.AutoField(primary_key=True)),
            ('target_ct', models.ForeignKey(orm['contenttypes.ContentType'], verbose_name=_('Target content type'))),
            ('target_id', models.PositiveIntegerField(_('Target id'))),
            ('subject', models.TextField(_('Comment subject'), max_length=defaults.SUBJECT_LENGTH)),
            ('content', models.TextField(_('Comment content'), max_length=defaults.COMMENT_LENGTH)),
            ('parent', models.ForeignKey(orm['comments.Comment'], null=True, verbose_name=_('Tree structure parent'), blank=True)),
            ('path', models.CharField(_('Genealogy tree path'), max_length=defaults.PATH_LENGTH, editable=False, blank=True)),
            ('user', models.ForeignKey(orm['auth.User'], null=True, verbose_name=_('Authorized author'), blank=True)),
            ('nickname', models.CharField(_("Anonymous author's nickname"), max_length=defaults.NICKNAME_LENGTH, blank=True)),
            ('email', models.EmailField(_('Authors email (optional)'), blank=True)),
            ('ip_address', models.IPAddressField(_('IP address'), null=True, blank=True)),
            ('submit_date', models.DateTimeField(_('Time submitted'), default=datetime.datetime.now, editable=True)),
            ('is_public', models.BooleanField(_('Is public'), default=True)),
        ))
        db.send_create_signal('comments', ['Comment'])

        # Adding model 'CommentOptions'
        db.create_table('comments_commentoptions', (
            ('id', models.AutoField(primary_key=True)),
            ('target_ct', models.ForeignKey(orm['contenttypes.ContentType'], verbose_name=_('Target content type'))),
            ('target_id', models.PositiveIntegerField(_('Target id'))),
            ('options', models.CharField(max_length=defaults.OPTS_LENGTH, blank=True)),
            ('timestamp', models.DateTimeField(default=datetime.datetime.now)),
        ))
        db.send_create_signal('comments', ['CommentOptions'])

        # Adding model 'BannedIP'
        db.create_table('comments_bannedip', (
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('comments', ['BannedIP'])



    def backwards(self, orm):

        # Deleting model 'BannedUser'
        db.delete_table('comments_banneduser')

        # Deleting model 'Comment'
        db.delete_table('comments_comment')

        # Deleting model 'CommentOptions'
        db.delete_table('comments_commentoptions')

        # Deleting model 'BannedIP'
        db.delete_table('comments_bannedip')



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
            'submit_date': ('models.DateTimeField', ["_('Time submitted')"], {'default': 'datetime.datetime.now', 'editable': 'True'}),
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
            'timestamp': ('models.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        'comments.banneduser': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'target_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'verbose_name': "_('Target content type')"}),
            'target_id': ('models.PositiveIntegerField', ["_('Target id')"], {}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'verbose_name': "_('Banned author')"})
        }
    }

    complete_apps = ['comments']
