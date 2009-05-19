# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from ella.answers.models import *

class Migration:
    
    depends_on = (
        ("core", "0001_initial"),
    )
 
    def forwards(self, orm):
        
        # Adding model 'Question'
        db.create_table('answers_question', (
            ('id', models.AutoField(primary_key=True)),
            ('text', models.CharField(_(u'Question'), max_length=200)),
            ('specification', models.TextField(_(u'Specification'))),
            ('nick', models.CharField(_('Nickname'), max_length=150)),
            ('created', models.DateTimeField(auto_now_add=True)),
            ('slug', models.SlugField()),
            ('timelimit', models.DateTimeField(default=get_default_timelimit)),
        ))
        db.send_create_signal('answers', ['Question'])
        
        # Adding model 'QuestionGroup'
        db.create_table('answers_questiongroup', (
            ('id', models.AutoField(primary_key=True)),
            ('site', models.ForeignKey(orm['sites.Site'])),
            ('default_timelimit', TimedeltaField()),
        ))
        db.send_create_signal('answers', ['QuestionGroup'])
        
        # Adding model 'Answer'
        db.create_table('answers_answer', (
            ('id', models.AutoField(primary_key=True)),
            ('text', models.TextField(_('Answer text'))),
            ('nick', models.CharField(_('Nickname'), max_length=150)),
            ('authorized_user', models.ForeignKey(orm['auth.User'], null=True, verbose_name=_('Authorized user'), blank=True)),
            ('created', models.DateTimeField(auto_now_add=True)),
            ('question', models.ForeignKey(orm.Question)),
            ('is_hidden', models.BooleanField(_('Is hidden'), default=False)),
        ))
        db.send_create_signal('answers', ['Answer'])
        
        # Adding ManyToManyField 'QuestionGroup.questions'
        db.create_table('answers_questiongroup_questions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('questiongroup', models.ForeignKey(orm.QuestionGroup, null=False)),
            ('question', models.ForeignKey(orm.Question, null=False))
        ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Question'
        db.delete_table('answers_question')
        
        # Deleting model 'QuestionGroup'
        db.delete_table('answers_questiongroup')
        
        # Deleting model 'Answer'
        db.delete_table('answers_answer')
        
        # Dropping ManyToManyField 'QuestionGroup.questions'
        db.delete_table('answers_questiongroup_questions')
        
    
    
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
