# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from ella.answers.models import *

class Migration:
    
    def forwards(self, orm):
        "Write your forwards migration here"
    
    
    def backwards(self, orm):
        "Write your backwards migration here"
    
    
    models = {
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'answers.question': {
            'Meta': {'ordering': "('-created',)"},
            'created': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'nick': ('models.CharField', ["_('Nickname')"], {'max_length': '150'}),
            'slug': ('models.SlugField', [], {}),
            'specification': ('models.TextField', ["_(u'Specification')"], {}),
            'text': ('models.CharField', ["_(u'Question')"], {'max_length': '200'}),
            'timelimit': ('models.DateTimeField', [], {'default': 'get_default_timelimit'})
        },
        'answers.questiongroup': {
            'default_timelimit': ('TimedeltaField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'questions': ('models.ManyToManyField', ["orm['answers.Question']"], {}),
            'site': ('models.ForeignKey', ["orm['sites.Site']"], {})
        },
        'answers.answer': {
            'Meta': {'ordering': "('-created',)", 'permissions': "(('can_answer_as_expert',_('Can answer as an expert')),)"},
            'authorized_user': ('models.ForeignKey', ["orm['auth.User']"], {'null': 'True', 'verbose_name': "_('Authorized user')", 'blank': 'True'}),
            'created': ('models.DateTimeField', [], {'auto_now_add': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'is_hidden': ('models.BooleanField', ["_('Is hidden')"], {'default': 'False'}),
            'nick': ('models.CharField', ["_('Nickname')"], {'max_length': '150'}),
            'question': ('models.ForeignKey', ["orm['answers.Question']"], {}),
            'text': ('models.TextField', ["_('Answer text')"], {})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'db_table': "'django_site'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    complete_apps = ['answers']
