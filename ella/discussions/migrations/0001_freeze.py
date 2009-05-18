
from south.db import db
from django.db import models
from ella.discussions.models import *

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
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'photos.photo': {
            'Meta': {'ordering': "('-created',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'discussions.topicthread': {
            'author': ('models.ForeignKey', ["orm['auth.User']"], {'null': 'True', 'verbose_name': "_('authorized author')", 'blank': 'True'}),
            'created': ('models.DateTimeField', ["_('Created')"], {'default': 'datetime.now', 'editable': 'False'}),
            'email': ('models.EmailField', ["_('Authors email (optional)')"], {'blank': 'True'}),
            'hit_counts': ('models.PositiveIntegerField', [], {'default': '0'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'nickname': ('models.CharField', ['_("Anonymous author\'s nickname")'], {'max_length': '50', 'blank': 'True'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '255'}),
            'topic': ('models.ForeignKey', ["orm['discussions.Topic']"], {})
        },
        'discussions.bannedstring': {
            'expression': ('models.CharField', ["_('Expression')"], {'max_length': '20', 'db_index': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'isregexp': ('models.BooleanField', [], {'default': 'False'})
        },
        'discussions.postviewed': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'target_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'verbose_name': "_('Target content type')"}),
            'target_id': ('models.PositiveIntegerField', ["_('Target id')"], {}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {})
        },
        'discussions.banneduser': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'related_name': "'banned_user'"})
        },
        'discussions.topic': {
            'Meta': {'ordering': "('-created',)"},
            'category': ('models.ForeignKey', ["orm['core.Category']"], {'verbose_name': "_('Category')"}),
            'created': ('models.DateTimeField', ["_('Created')"], {'default': 'datetime.now', 'editable': 'False'}),
            'description': ('models.TextField', ["_('Description')"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'photo': ('models.ForeignKey', ["orm['photos.Photo']"], {'null': 'True', 'verbose_name': "_('Photo')", 'blank': 'True'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '255'})
        }
    }
    
    complete_apps = ['discussions']
