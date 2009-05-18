
from south.db import db
from django.db import models
from ella.interviews.models import *

class Migration:
    
    def forwards(self, orm):
        "Write your forwards migration here"
    
    
    def backwards(self, orm):
        "Write your backwards migration here"
    
    
    models = {
        'core.category': {
            'Meta': {'ordering': "('site','tree_path',)", 'unique_together': "(('site','tree_path'),)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'interviews.answer': {
            'Meta': {'ordering': "('-submit_date',)"},
            'content': ('models.TextField', ["_('Answer text')"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'interviewee': ('models.ForeignKey', ["orm['interviews.Interviewee']"], {}),
            'question': ('models.ForeignKey', ["orm['interviews.Question']"], {}),
            'submit_date': ('models.DateTimeField', ["_('date/time submitted')"], {'default': 'datetime.now'})
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
        'interviews.interviewee': {
            'Meta': {'ordering': "('name',)"},
            'author': ('models.ForeignKey', ["orm['core.Author']"], {'null': 'True', 'blank': 'True'}),
            'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ["_('Name')"], {'max_length': '200', 'blank': 'True'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'null': 'True', 'blank': 'True'})
        },
        'core.author': {
            'Meta': {'ordering': "('name','slug',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.source': {
            'Meta': {'ordering': "('name',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'interviews.interview': {
            'Meta': {'ordering': "('-ask_from',)"},
            'ask_from': ('models.DateTimeField', ["_('Ask from')"], {}),
            'ask_to': ('models.DateTimeField', ["_('Ask to')"], {}),
            'authors': ('models.ManyToManyField', ["orm['core.Author']"], {'verbose_name': "_('Authors')"}),
            'category': ('models.ForeignKey', ["orm['core.Category']"], {'verbose_name': "_('Category')"}),
            'content': ('models.TextField', ["_('Text')"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'interviewees': ('models.ManyToManyField', ["orm['interviews.Interviewee']"], {'verbose_name': "_('Interviewees')"}),
            'perex': ('models.TextField', ["_('Perex')"], {}),
            'photo': ('models.ForeignKey', ["orm['photos.Photo']"], {'null': 'True', 'verbose_name': "_('Photo')", 'blank': 'True'}),
            'reply_from': ('models.DateTimeField', ["_('Reply from')"], {}),
            'reply_to': ('models.DateTimeField', ["_('Reply to')"], {}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'source': ('models.ForeignKey', ["orm['core.Source']"], {'null': 'True', 'verbose_name': "_('Source')", 'blank': 'True'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '255'}),
            'upper_title': ('models.CharField', ["_('Upper title')"], {'max_length': '255', 'blank': 'True'})
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
            'submit_date': ('models.DateTimeField', ["_('date/time submitted')"], {'default': 'datetime.now', 'editable': 'True'}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'related_name': "'interview_question_set'", 'null': 'True', 'verbose_name': "_('authorized author')", 'blank': 'True'})
        }
    }
    
    complete_apps = ['interviews']
