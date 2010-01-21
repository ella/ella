
from south.db import db
from django.db import models
from ella.attachments.models import *
import datetime

class Migration:

    depends_on = (
        ("photos", "0001_initial"),
    )
     
    def forwards(self, orm):
        
        # Adding model 'Type'
        db.create_table('attachments_type', (
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(_('Name'), max_length=100)),
            ('mimetype', models.CharField(_('Mime type'), max_length=100)),
        ))
        db.send_create_signal('attachments', ['Type'])
        
        # Adding model 'Attachment'
        db.create_table('attachments_attachment', (
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(_('Name'), max_length=255)),
            ('slug', models.SlugField(_('Slug'), max_length=255)),
            ('photo', models.ForeignKey(orm['photos.Photo'], null=True, verbose_name=_('Photo'), blank=True)),
            ('description', models.TextField(_('Description'))),
            ('created', models.DateTimeField(_('Created'), default=datetime.datetime.now, editable=False)),
            ('attachment', models.FileField(_('Attachment'))),
            ('type', models.ForeignKey(orm.Type, verbose_name=_('Attachment type'))),
        ))
        db.send_create_signal('attachments', ['Attachment'])
        
        # Creating unique_together for [name, mimetype] on Type.
        db.create_unique('attachments_type', ['name', 'mimetype'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Type'
        db.delete_table('attachments_type')
        
        # Deleting model 'Attachment'
        db.delete_table('attachments_attachment')
        
        # Deleting unique_together for [name, mimetype] on Type.
        db.delete_unique('attachments_type', ['name', 'mimetype'])
        
    
    
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
            'created': ('models.DateTimeField', ["_('Created')"], {'default': 'datetime.datetime.now', 'editable': 'False'}),
            'description': ('models.TextField', ["_('Description')"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ["_('Name')"], {'max_length': '255'}),
            'photo': ('models.ForeignKey', ["orm['photos.Photo']"], {'null': 'True', 'verbose_name': "_('Photo')", 'blank': 'True'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'type': ('models.ForeignKey', ["orm['attachments.Type']"], {'verbose_name': "_('Attachment type')"})
        }
    }
    
    complete_apps = ['attachments']
