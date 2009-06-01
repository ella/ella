
from south.db import db
from django.db import models
from ella.interviews.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Changing field 'Question.submit_date'
        db.alter_column('interviews_question', 'submit_date', models.DateTimeField(_('date/time submitted'), default=datetime.now, editable=False))
        
    
    
    def backwards(self, orm):
        
        # Changing field 'Question.submit_date'
        db.alter_column('interviews_question', 'submit_date', models.DateTimeField(_('date/time submitted'), default=datetime.now, editable=True))
        
    
    
    models = {
        'interviews.question': {
            'Meta': {'ordering': "('submit_date',)"},
            'content': ('models.TextField', ["_('Question text')"], {}),
            'email': ('models.EmailField', ["_('authors email (optional)')"], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'interview': ('models.ForeignKey', ["orm['interviews.Interview']"], {}),
            'ip_address': ('models.IPAddressField', ["_('ip address')"], {'null': 'True', 'blank': 'True'}),
            'is_public': ('models.BooleanField', ["_('is public')"], {'default': 'True'}),
            'nickname': ('models.CharField', ['_("anonymous author\'s nickname")'], {'max_length': '200', 'blank': 'True'}),
            'submit_date': ('models.DateTimeField', ["_('date/time submitted')"], {'default': 'datetime.now', 'editable': 'False'}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'related_name': "'interview_question_set'", 'null': 'True', 'verbose_name': "_('authorized author')", 'blank': 'True'})
        }
    }
    
    complete_apps = ['interviews']
