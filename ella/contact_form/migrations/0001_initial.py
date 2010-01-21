
from south.db import db
from django.db import models
from ella.contact_form.models import *
import datetime

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Recipient'
        db.create_table('contact_form_recipient', (
            ('id', models.AutoField(primary_key=True)),
            ('email', models.EmailField(_("Email"))),
        ))
        db.send_create_signal('contact_form', ['Recipient'])
        
        # Adding model 'Message'
        db.create_table('contact_form_message', (
            ('id', models.AutoField(primary_key=True)),
            ('sender', models.EmailField(_("Sender email"), blank=True)),
            ('subject', models.CharField(_("Subject"), max_length=255, blank=True)),
            ('content', models.TextField(_("Message content"))),
            ('created', models.DateTimeField(_('Created'), default=datetime.datetime.now, editable=False)),
        ))
        db.send_create_signal('contact_form', ['Message'])
        
        # Adding ManyToManyField 'Recipient.sites'
        db.create_table('contact_form_recipient_sites', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('recipient', models.ForeignKey(orm.Recipient, null=False)),
            ('site', models.ForeignKey(orm['sites.Site'], null=False))
        ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Recipient'
        db.delete_table('contact_form_recipient')
        
        # Deleting model 'Message'
        db.delete_table('contact_form_message')
        
        # Dropping ManyToManyField 'Recipient.sites'
        db.delete_table('contact_form_recipient_sites')
        
    
    
    models = {
        'contact_form.recipient': {
            'email': ('models.EmailField', ['_("Email")'], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'sites': ('models.ManyToManyField', ["orm['sites.Site']"], {})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'db_table': "'django_site'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'contact_form.message': {
            'content': ('models.TextField', ['_("Message content")'], {}),
            'created': ('models.DateTimeField', ["_('Created')"], {'default': 'datetime.datetime.now', 'editable': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'sender': ('models.EmailField', ['_("Sender email")'], {'blank': 'True'}),
            'subject': ('models.CharField', ['_("Subject")'], {'max_length': '255', 'blank': 'True'})
        }
    }
    
    complete_apps = ['contact_form']
