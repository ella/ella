
from south.db import db
from django.db import models
from ella.attachments.models import *

class Migration:
    
    def forwards(self, orm):
        "Write your forwards migration here"
    
    
    def backwards(self, orm):
        "Write your backwards migration here"
    
    
    models = {
        'photos.photo': {
            'Meta': {'ordering': "('-created',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'attachments.type': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('name','mimetype'),)"},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('models.CharField', ["_('Mime type')"], {'max_length': '100'}),
            'name': ('models.CharField', ["_('Name')"], {'max_length': '100'})
        },
        'attachments.attachment': {
            'Meta': {'ordering': "('created',)"},
            'attachment': ('models.FileField', ["_('Attachment')"], {}),
            'created': ('models.DateTimeField', ["_('Created')"], {'default': 'datetime.now', 'editable': 'False'}),
            'description': ('models.TextField', ["_('Description')"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ["_('Name')"], {'max_length': '255'}),
            'photo': ('models.ForeignKey', ["orm['photos.Photo']"], {'null': 'True', 'verbose_name': "_('Photo')", 'blank': 'True'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'type': ('models.ForeignKey', ["orm['attachments.Type']"], {'verbose_name': "_('Attachment type')"})
        }
    }
    
    complete_apps = ['attachments']
