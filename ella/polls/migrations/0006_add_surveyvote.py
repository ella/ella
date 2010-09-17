
from south.db import db
from django.db import models
from ella.polls.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'SurveyVote'
        db.create_table('polls_surveyvote', (
            ('id', orm['polls.surveyvote:id']),
            ('survey', orm['polls.surveyvote:survey']),
            ('user', orm['polls.surveyvote:user']),
            ('time', orm['polls.surveyvote:time']),
            ('ip_address', orm['polls.surveyvote:ip_address']),
        ))
        db.send_create_signal('polls', ['SurveyVote'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'SurveyVote'
        db.delete_table('polls_surveyvote')
        
    
    
    models = {
        'auth.group': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('models.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('models.CharField', [], {'max_length': '100'}),
            'content_type': ('models.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('models.CharField', [], {'max_length': '100'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'model': ('models.CharField', [], {'max_length': '100'}),
            'name': ('models.CharField', [], {'max_length': '100'})
        },
        'core.author': {
            'description': ('models.TextField', [], {'blank': 'True'}),
            'email': ('models.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'slug': ('models.SlugField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'text': ('models.TextField', [], {'blank': 'True'}),
            'user': ('models.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'core.category': {
            'Meta': {'unique_together': "(('site', 'tree_path'),)"},
            'description': ('models.TextField', [], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'site': ('models.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('models.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'title': ('models.CharField', [], {'max_length': '200'}),
            'tree_parent': ('models.ForeignKey', [], {'to': "orm['core.Category']", 'null': 'True', 'blank': 'True'}),
            'tree_path': ('models.CharField', [], {'max_length': '255'})
        },
        'core.publishable': {
            'Meta': {'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.source': {
            'description': ('models.TextField', [], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '200'}),
            'url': ('models.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'photos.photo': {
            'Meta': {'ordering': "('-created',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
        },
        'polls.choice': {
            'choice': ('models.TextField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'points': ('models.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'question': ('models.ForeignKey', [], {'to': "orm['polls.Question']"}),
            'votes': ('models.IntegerField', [], {'default': '0', 'blank': 'True'})
        },
        'polls.contest': {
            'active_from': ('models.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'active_till': ('models.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'publishable_ptr': ('models.OneToOneField', [], {'to': "orm['core.Publishable']", 'unique': 'True', 'primary_key': 'True'}),
            'text': ('models.TextField', [], {}),
            'text_announcement': ('models.TextField', [], {'default': "''", 'blank': 'True'}),
            'text_results': ('models.TextField', [], {})
        },
        'polls.contestant': {
            'Meta': {'unique_together': "(('contest', 'email'),)"},
            'address': ('models.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'choices': ('models.TextField', [], {'blank': 'True'}),
            'contest': ('models.ForeignKey', [], {'to': "orm['polls.Contest']"}),
            'count_guess': ('models.IntegerField', [], {}),
            'datetime': ('models.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('models.EmailField', [], {'max_length': '75'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '200'}),
            'phonenumber': ('models.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'surname': ('models.CharField', [], {'max_length': '200'}),
            'user': ('models.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'winner': ('models.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'polls.poll': {
            'active_from': ('models.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'active_till': ('models.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'question': ('models.ForeignKey', [], {'to': "orm['polls.Question']", 'unique': 'True'}),
            'text': ('models.TextField', [], {}),
            'text_announcement': ('models.TextField', [], {'default': "''", 'blank': 'True'}),
            'text_results': ('models.TextField', [], {}),
            'title': ('models.CharField', [], {'max_length': '200'})
        },
        'polls.question': {
            'allow_multiple': ('models.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_no_choice': ('models.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'contest': ('models.ForeignKey', [], {'to': "orm['polls.Contest']", 'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'question': ('models.TextField', [], {}),
            'quiz': ('models.ForeignKey', [], {'to': "orm['polls.Quiz']", 'null': 'True', 'blank': 'True'})
        },
        'polls.quiz': {
            'active_from': ('models.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'active_till': ('models.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'has_correct_answers': ('models.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'publishable_ptr': ('models.OneToOneField', [], {'to': "orm['core.Publishable']", 'unique': 'True', 'primary_key': 'True'}),
            'text': ('models.TextField', [], {}),
            'text_announcement': ('models.TextField', [], {'default': "''", 'blank': 'True'}),
            'text_results': ('models.TextField', [], {})
        },
        'polls.result': {
            'count': ('models.IntegerField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'points_from': ('models.IntegerField', [], {'null': 'True'}),
            'points_to': ('models.IntegerField', [], {'null': 'True'}),
            'quiz': ('models.ForeignKey', [], {'to': "orm['polls.Quiz']"}),
            'text': ('models.TextField', [], {}),
            'title': ('models.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'polls.survey': {
            'active_from': ('models.DateTimeField', [], {}),
            'active_till': ('models.DateTimeField', [], {}),
            'question_ptr': ('models.OneToOneField', [], {'to': "orm['polls.Question']", 'unique': 'True', 'primary_key': 'True'})
        },
        'polls.surveyvote': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('models.IPAddressField', [], {'max_length': '15', 'null': 'True'}),
            'survey': ('models.ForeignKey', [], {'to': "orm['polls.Survey']"}),
            'time': ('models.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('models.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'polls.vote': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('models.IPAddressField', [], {'max_length': '15', 'null': 'True'}),
            'poll': ('models.ForeignKey', [], {'to': "orm['polls.Poll']"}),
            'time': ('models.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('models.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'sites.site': {
            'Meta': {'db_table': "'django_site'"},
            'domain': ('models.CharField', [], {'max_length': '100'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '50'})
        }
    }
    
    complete_apps = ['polls']
