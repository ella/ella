
from south.db import db
from django.db import models
from ella.ellaexports.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'AggregatedExport'
        db.create_table('ellaexports_aggregatedexport', (
            ('id', orm['ellaexports.aggregatedexport:id']),
            ('title', orm['ellaexports.aggregatedexport:title']),
            ('description', orm['ellaexports.aggregatedexport:description']),
            ('slug', orm['ellaexports.aggregatedexport:slug']),
        ))
        db.send_create_signal('ellaexports', ['AggregatedExport'])
        
        # Adding ManyToManyField 'AggregatedExport.exports'
        db.create_table('ellaexports_aggregatedexport_exports', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('aggregatedexport', models.ForeignKey(orm.AggregatedExport, null=False)),
            ('export', models.ForeignKey(orm.Export, null=False))
        ))
        
        # Creating unique_together for [title] on AggregatedExport.
        db.create_unique('ellaexports_aggregatedexport', ['title'])
        
        # Creating unique_together for [slug] on AggregatedExport.
        db.create_unique('ellaexports_aggregatedexport', ['slug'])
        
    
    
    def backwards(self, orm):
        
        # Deleting unique_together for [slug] on AggregatedExport.
        db.delete_unique('ellaexports_aggregatedexport', ['slug'])
        
        # Deleting unique_together for [title] on AggregatedExport.
        db.delete_unique('ellaexports_aggregatedexport', ['title'])
        
        # Deleting model 'AggregatedExport'
        db.delete_table('ellaexports_aggregatedexport')
        
        # Dropping ManyToManyField 'AggregatedExport.exports'
        db.delete_table('ellaexports_aggregatedexport_exports')
        
    
    
    models = {
        'auth.group': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('models.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('models.CharField', [], {'max_length': '100'}),
            'content_type': ('models.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('models.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('models.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('models.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('models.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('models.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('models.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('models.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('models.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('models.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('models.CharField', [], {'max_length': '128'}),
            'user_permissions': ('models.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('models.CharField', [], {'unique': 'True', 'max_length': '30'})
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
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
        },
        'core.publishable': {
            'Meta': {'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
        },
        'core.source': {
            'description': ('models.TextField', [], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '200'}),
            'url': ('models.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'ellaexports.aggregatedexport': {
            'Meta': {'unique_together': "(('title',), ('slug',))"},
            'description': ('models.TextField', [], {'blank': 'True'}),
            'exports': ('models.ManyToManyField', [], {'to': "orm['ellaexports.Export']", 'symmetrical': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'slug': ('models.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'title': ('models.CharField', [], {'max_length': '255'})
        },
        'ellaexports.export': {
            'Meta': {'unique_together': "(('title',), ('slug',))"},
            'category': ('models.ForeignKey', [], {'to': "orm['core.Category']"}),
            'description': ('models.TextField', [], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'max_visible_items': ('models.IntegerField', [], {}),
            'photo_format': ('models.ForeignKey', [], {'to': "orm['photos.Format']"}),
            'slug': ('models.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'title': ('models.CharField', [], {'max_length': '255'}),
            'use_objects_in_category': ('models.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'ellaexports.exportmeta': {
            'description': ('models.TextField', [], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'photo': ('models.ForeignKey', [], {'to': "orm['photos.Photo']", 'null': 'True', 'blank': 'True'}),
            'publishable': ('models.ForeignKey', [], {'to': "orm['core.Publishable']"}),
            'title': ('models.CharField', [], {'max_length': '64', 'blank': 'True'})
        },
        'ellaexports.exportposition': {
            'export': ('models.ForeignKey', [], {'to': "orm['ellaexports.Export']"}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'object': ('models.ForeignKey', [], {'to': "orm['ellaexports.ExportMeta']"}),
            'position': ('models.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'visible_from': ('models.DateTimeField', [], {}),
            'visible_to': ('models.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'oldcomments.comment': {
            'Meta': {'db_table': "'comments_comment'"},
            'content': ('models.TextField', [], {'max_length': '3000'}),
            'email': ('models.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('models.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'is_public': ('models.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'nickname': ('models.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'parent': ('models.ForeignKey', [], {'to': "orm['oldcomments.Comment']", 'null': 'True', 'blank': 'True'}),
            'path': ('models.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'subject': ('models.TextField', [], {'max_length': '100'}),
            'submit_date': ('models.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'target_ct': ('models.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'target_id': ('models.PositiveIntegerField', [], {}),
            'user': ('models.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'photos.format': {
            'flexible_height': ('models.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'flexible_max_height': ('models.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'max_height': ('models.PositiveIntegerField', [], {}),
            'max_width': ('models.PositiveIntegerField', [], {}),
            'name': ('models.CharField', [], {'max_length': '80'}),
            'nocrop': ('models.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'resample_quality': ('models.IntegerField', [], {'default': '85'}),
            'sites': ('models.ManyToManyField', [], {'to': "orm['sites.Site']", 'symmetrical': 'False'}),
            'stretch': ('models.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'photos.photo': {
            'Meta': {'ordering': "('-created',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
        },
        'sites.site': {
            'Meta': {'db_table': "'django_site'"},
            'domain': ('models.CharField', [], {'max_length': '100'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '50'})
        }
    }
    
    complete_apps = ['ellaexports']
