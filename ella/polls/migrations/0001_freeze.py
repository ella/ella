
from south.db import db
from django.db import models
from ella.polls.models import *

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
        'polls.choice': {
            'choice': ('models.TextField', ["_('Choice text')"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'points': ('models.IntegerField', ["_('Points')"], {'null': 'True', 'blank': 'False'}),
            'question': ('models.ForeignKey', ["orm['polls.Question']"], {'verbose_name': "_('Question')"}),
            'votes': ('models.IntegerField', ["_('Votes')"], {'null': 'True', 'blank': 'True'})
        },
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'polls.contest': {
            'Meta': {'ordering': "('-active_from',)"},
            'active_from': ('models.DateTimeField', ["_('Active from')"], {}),
            'active_till': ('models.DateTimeField', ["_('Active till')"], {}),
            'category': ('models.ForeignKey', ["orm['core.Category']"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'photo': ('models.ForeignKey', ["orm['photos.Photo']"], {}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'text': ('models.TextField', ["_('Text')"], {}),
            'text_announcement': ('models.TextField', ["_('Text with announcement')"], {}),
            'text_results': ('models.TextField', ["_('Text with results')"], {}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '200'})
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
            'active_from': ('models.DateTimeField', ["_('Active from')"], {'default': 'datetime.now', 'null': 'True', 'blank': 'True'}),
            'active_till': ('models.DateTimeField', ["_('Active till')"], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'question': ('models.ForeignKey', ["orm['polls.Question']"], {'unique': 'True', 'verbose_name': "_('Question')"}),
            'text': ('models.TextField', ["_('Text')"], {'null': 'True', 'blank': 'True'}),
            'text_announcement': ('models.TextField', ["_('Text with announcement')"], {'null': 'True', 'blank': 'True'}),
            'text_results': ('models.TextField', ["_('Text with results')"], {'null': 'True', 'blank': 'True'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '200'})
        },
        'photos.photo': {
            'Meta': {'ordering': "('-created',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.author': {
            'Meta': {'ordering': "('name','slug',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'polls.quiz': {
            'Meta': {'ordering': "('-active_from',)"},
            'active_from': ('models.DateTimeField', ["_('Active from')"], {}),
            'active_till': ('models.DateTimeField', ["_('Active till')"], {}),
            'authors': ('models.ManyToManyField', ["orm['core.Author']"], {'verbose_name': "_('Authors')"}),
            'category': ('models.ForeignKey', ["orm['core.Category']"], {}),
            'has_correct_answers': ('models.BooleanField', ["_('Has correct answers')"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'photo': ('models.ForeignKey', ["orm['photos.Photo']"], {}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'text': ('models.TextField', ["_('Text')"], {}),
            'text_announcement': ('models.TextField', ["_('text with announcement')"], {}),
            'text_results': ('models.TextField', ["_('Text with results')"], {}),
            'title': ('models.CharField', ["_('title')"], {'max_length': '200'})
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
