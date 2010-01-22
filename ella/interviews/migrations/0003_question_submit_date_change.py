
from south.db import db
from django.db import models
from ella.interviews.models import *
import datetime

class Migration:
    
    def forwards(self, orm):
        
        # Changing field 'Question.submit_date'
        db.alter_column('interviews_question', 'submit_date', models.DateTimeField(_('date/time submitted'), default=datetime.datetime.now, editable=False))
        
    
    
    def backwards(self, orm):
        
        # Changing field 'Question.submit_date'
        db.alter_column('interviews_question', 'submit_date', models.DateTimeField(_('date/time submitted'), default=datetime.datetime.now, editable=True))
        
    
    
    models = {
        'core.category': {
            'Meta': {'unique_together': "(('site','tree_path'),)", 'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'interviews.answer': {
            'content': ('models.TextField', ["_('Answer text')"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'interviewee': ('models.ForeignKey', ["orm['interviews.Interviewee']"], {}),
            'question': ('models.ForeignKey', ["orm['interviews.Question']"], {}),
            'submit_date': ('models.DateTimeField', ["_('date/time submitted')"], {'default': 'datetime.datetime.now'})
        },
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'photos.photo': {
            'Meta': {'ordering': "('-created',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'interviews.interview': {
            'Meta': {'ordering': "('-ask_from',)", '_bases': ['ella.core.models.publishable.Publishable']},
            'ask_from': ('models.DateTimeField', ["_('Ask from')"], {}),
            'ask_to': ('models.DateTimeField', ["_('Ask to')"], {}),
            'content': ('models.TextField', ["_('Text')"], {}),
            'interviewees': ('models.ManyToManyField', ["orm['interviews.Interviewee']"], {'verbose_name': "_('Interviewees')"}),
            'publishable_ptr': ('models.OneToOneField', ["orm['core.Publishable']"], {}),
            'reply_from': ('models.DateTimeField', ["_('Reply from')"], {}),
            'reply_to': ('models.DateTimeField', ["_('Reply to')"], {}),
            'upper_title': ('models.CharField', ["_('Upper title')"], {'max_length': '255', 'blank': 'True'})
        },
        'core.author': {
            'Meta': {'ordering': "('name','slug',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.publishable': {
            'Meta': {'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.source': {
            'Meta': {'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'interviews.interviewee': {
            'Meta': {'ordering': "('name',)"},
            'author': ('models.ForeignKey', ["orm['core.Author']"], {'null': 'True', 'blank': 'True'}),
            'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ["_('Name')"], {'max_length': '200', 'blank': 'True'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'null': 'True', 'blank': 'True'})
        },
        'interviews.question': {
            'Meta': {'ordering': "('submit_date',)"},
            'content': ('models.TextField', ["_('Question text')"], {}),
            'email': ('models.EmailField', ["_('authors email (optional)')"], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'interview': ('models.ForeignKey', ["orm['interviews.Interview']"], {}),
            'ip_address': ('models.IPAddressField', ["_('ip address')"], {'null': 'True', 'blank': 'True'}),
            'is_public': ('models.BooleanField', ["_('is public')"], {'default': 'True'}),
            'nickname': ('models.CharField', ['_("anonymous author\'s nickname")'], {'max_length': '200', 'blank': 'True'}),
            'submit_date': ('models.DateTimeField', ["_('date/time submitted')"], {'default': 'datetime.datetime.now', 'editable': 'False'}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'related_name': "'interview_question_set'", 'null': 'True', 'verbose_name': "_('authorized author')", 'blank': 'True'})
        }
    }
    
    complete_apps = ['interviews']
