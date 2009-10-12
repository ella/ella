
from south.db import db
from django.db import models
from ella.polls.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Survey'
        db.create_table('polls_survey', (
            ('question_ptr', models.OneToOneField(orm['polls.Question'])),
            ('active_from', models.DateTimeField(_('Active from'))),
            ('active_till', models.DateTimeField(_('Active till'))),
        ))
        db.send_create_signal('polls', ['Survey'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Survey'
        db.delete_table('polls_survey')
        
    
    
    models = {
        'core.category': {
            'Meta': {'unique_together': "(('site','tree_path'),)", 'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'polls.choice': {
            'choice': ('models.TextField', ["_('Choice text')"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'points': ('models.IntegerField', ["_('Points')"], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'question': ('models.ForeignKey', ["orm['polls.Question']"], {'verbose_name': "_('Question')"}),
            'votes': ('models.IntegerField', ["_('Votes')"], {'default': '0', 'blank': 'True'})
        },
        'polls.survey': {
            'Meta': {'ordering': "('-active_from',)", '_bases': ['ella.polls.models.Question']},
            'active_from': ('models.DateTimeField', ["_('Active from')"], {}),
            'active_till': ('models.DateTimeField', ["_('Active till')"], {}),
            'question_ptr': ('models.OneToOneField', ["orm['polls.Question']"], {})
        },
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'polls.contest': {
            'Meta': {'ordering': "('-active_from',)", '_bases': ['ella.core.models.publishable.Publishable']},
            'active_from': ('models.DateTimeField', ["_('Active from')"], {'null': 'True', 'blank': 'True'}),
            'active_till': ('models.DateTimeField', ["_('Active till')"], {'null': 'True', 'blank': 'True'}),
            'publishable_ptr': ('models.OneToOneField', ["orm['core.Publishable']"], {}),
            'text': ('models.TextField', ["_('Text')"], {}),
            'text_announcement': ('models.TextField', ["_('Text with announcement')"], {}),
            'text_results': ('models.TextField', ["_('Text with results')"], {})
        },
        'polls.vote': {
            'Meta': {'ordering': "('-time',)"},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('models.IPAddressField', ["_('IP Address')"], {'null': 'True'}),
            'poll': ('models.ForeignKey', ["orm['polls.Poll']"], {'verbose_name': "_('Poll')"}),
            'time': ('models.DateTimeField', ["_('Time')"], {'auto_now': 'True'}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'null': 'True', 'verbose_name': "_('User')", 'blank': 'True'})
        },
        'polls.result': {
            'count': ('models.IntegerField', ["_('Count')"], {'null': 'False', 'blank': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'points_from': ('models.IntegerField', ["_('Points dimension from')"], {'null': 'True'}),
            'points_to': ('models.IntegerField', ["_('Points dimension to')"], {'null': 'True'}),
            'quiz': ('models.ForeignKey', ["orm['polls.Quiz']"], {'verbose_name': "_('Quiz')"}),
            'text': ('models.TextField', ["_('Quiz results text')"], {}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '200', 'blank': 'True'})
        },
        'polls.question': {
            'allow_multiple': ('models.BooleanField', ["_('Allow multiple choices')"], {'default': 'False'}),
            'allow_no_choice': ('models.BooleanField', ["_('Allow no choice')"], {'default': 'False'}),
            'contest': ('models.ForeignKey', ["orm['polls.Contest']"], {'null': 'True', 'verbose_name': "_('Contest')", 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'question': ('models.TextField', ["_('Question text')"], {}),
            'quiz': ('models.ForeignKey', ["orm['polls.Quiz']"], {'null': 'True', 'verbose_name': "_('Quiz')", 'blank': 'True'})
        },
        'polls.poll': {
            'Meta': {'ordering': "('-active_from',)"},
            'active_from': ('models.DateTimeField', ["_('Active from')"], {'null': 'True', 'blank': 'True'}),
            'active_till': ('models.DateTimeField', ["_('Active till')"], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'question': ('models.ForeignKey', ["orm['polls.Question']"], {'unique': 'True', 'verbose_name': "_('Question')"}),
            'text': ('models.TextField', ["_('Text')"], {}),
            'text_announcement': ('models.TextField', ["_('Text with announcement')"], {}),
            'text_results': ('models.TextField', ["_('Text with results')"], {}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '200'})
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
        'photos.photo': {
            'Meta': {'ordering': "('-created',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.source': {
            'Meta': {'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'polls.surveyvote': {
            'Meta': {'ordering': "('-time',)"},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('models.IPAddressField', ["_('IP Address')"], {'null': 'True'}),
            'survey': ('models.ForeignKey', ["orm['polls.Survey']"], {'verbose_name': "_('Survey')"}),
            'time': ('models.DateTimeField', ["_('Time')"], {'auto_now': 'True'}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'null': 'True', 'verbose_name': "_('User')", 'blank': 'True'})
        },
        'core.author': {
            'Meta': {'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'polls.quiz': {
            'Meta': {'ordering': "('-active_from',)", '_bases': ['ella.core.models.publishable.Publishable']},
            'active_from': ('models.DateTimeField', ["_('Active from')"], {'null': 'True', 'blank': 'True'}),
            'active_till': ('models.DateTimeField', ["_('Active till')"], {'null': 'True', 'blank': 'True'}),
            'has_correct_answers': ('models.BooleanField', ["_('Has correct answers')"], {}),
            'publishable_ptr': ('models.OneToOneField', ["orm['core.Publishable']"], {}),
            'text': ('models.TextField', ["_('Text')"], {}),
            'text_announcement': ('models.TextField', ["_('Text with announcement')"], {}),
            'text_results': ('models.TextField', ["_('Text with results')"], {})
        },
        'polls.contestant': {
            'Meta': {'ordering': "('-datetime',)", 'unique_together': "(('contest','email',),)"},
            'address': ('models.CharField', ["_('Address')"], {'max_length': '200', 'blank': 'True'}),
            'choices': ('models.TextField', ["_('Choices')"], {'blank': 'True'}),
            'contest': ('models.ForeignKey', ["orm['polls.Contest']"], {'verbose_name': "_('Contest')"}),
            'count_guess': ('models.IntegerField', ["_('Count guess')"], {}),
            'datetime': ('models.DateTimeField', ["_('Date and time')"], {'auto_now_add': 'True'}),
            'email': ('models.EmailField', ["_('email')"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ["_('First name')"], {'max_length': '200'}),
            'phonenumber': ('models.CharField', ["_('Phone number')"], {'max_length': '20', 'blank': 'True'}),
            'surname': ('models.CharField', ["_('Last name')"], {'max_length': '200'}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'null': 'True', 'verbose_name': "_('User')", 'blank': 'True'}),
            'winner': ('models.BooleanField', ["_('Winner')"], {'default': 'False'})
        }
    }
    
    complete_apps = ['polls']
