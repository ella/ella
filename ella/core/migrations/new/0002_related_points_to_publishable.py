
from south.db import db
from django.db import models
from ella.core.models import *

class Migration:
    
    def forwards(self, orm):
        db.add_column('core_related', 'publishable', models.ForeignKey(orm.Publishable, verbose_name=_('Publishable')))

        orm.Related.objects.extra(
                tables=['core_publishable'],
                where=[
                    'core_publishable.content_type_id = core_related.source_ct_id',
                    'core_publishable.id = core_related.source_id',
                ]
            ).update(publishable_id=models.F('id'), source_id=0)
        orm.Publishable.objects.exclude(source_id=0).delete()


        db.delete_column('core_related', 'source_ct_id')
        db.delete_column('core_related', 'source_id')
        db.rename_column('core_related', 'target_id', 'related_id')
        db.rename_column('core_related', 'target_ct_id', 'related_ct_it')
        
    def backwards(self, orm):
        db.add_column('core_related', 'source_ct', models.ForeignKey(orm.ContentType, verbose_name=_('Content type'), related_name='related_on_set'))
        db.add_column('core_nation', 'source_id', models.IntegerField(_('Object ID')))

        for r in orm.Related.objects.all():
            r.source_ct = r.publishable.content_type
            r.source_id = r.publishable.id
            r.save()

        db.delete_column('core_related', 'publishable_id')
        db.rename_column('core_related', 'related_id', 'target_id')
        db.rename_column('core_related', 'related_ct_it', 'target_ct_id')
    
    
    models = {
        'core.category': {
            'Meta': {'unique_together': "(('site','tree_path'),)", 'app_label': "'core'"},
            'description': ('models.TextField', ['_("Category Description")'], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'site': ('models.ForeignKey', ['Site'], {}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'title': ('models.CharField', ['_("Category Title")'], {'max_length': '200'}),
            'tree_parent': ('models.ForeignKey', ["'self'"], {'null': 'True', 'verbose_name': '_("Parent Category")', 'blank': 'True'}),
            'tree_path': ('models.CharField', [], {'editable': 'False', 'max_length': '255', 'verbose_name': '_("Path from root category")'})
        },
        'core.placement': {
            'Meta': {'app_label': "'core'"},
            'category': ('models.ForeignKey', ['Category'], {'verbose_name': "_('Category')", 'db_index': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'publish_from': ('models.DateTimeField', ['_("Start of visibility")'], {}),
            'publish_to': ('models.DateTimeField', ['_("End of visibility")'], {'null': 'True', 'blank': 'True'}),
            'publishable': ('models.ForeignKey', ['Publishable'], {'verbose_name': "_('Publishable object')"}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255', 'blank': 'True'}),
            'static': ('models.BooleanField', ["_('static')"], {'default': 'False'})
        },
        'core.listing': {
            'Meta': {'ordering': "('-publish_from',)", 'app_label': "'core'"},
            'category': ('models.ForeignKey', ['Category'], {'verbose_name': "_('Category')", 'db_index': 'True'}),
            'commercial': ('models.BooleanField', ['_("Commercial")'], {'default': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'placement': ('models.ForeignKey', ['Placement'], {'verbose_name': "_('Placement')"}),
            'priority_from': ('models.DateTimeField', ['_("Start of prioritized listing")'], {'null': 'True', 'blank': 'True'}),
            'priority_to': ('models.DateTimeField', ['_("End of prioritized listing")'], {'null': 'True', 'blank': 'True'}),
            'priority_value': ('models.IntegerField', ['_("Priority")'], {'null': 'True', 'blank': 'True'}),
            'publish_from': ('models.DateTimeField', ['_("Start of listing")'], {}),
            'publish_to': ('models.DateTimeField', ['_("End of listing")'], {'null': 'True', 'blank': 'True'})
        },
        'core.hitcount': {
            'Meta': {'app_label': "'core'"},
            'hits': ('models.PositiveIntegerField', ["_('Hits')"], {'default': '1'}),
            'last_seen': ('models.DateTimeField', ["_('Last seen')"], {'editable': 'False'}),
            'placement': ('models.ForeignKey', ['Placement'], {'primary_key': 'True'})
        },
        'core.related': {
            'Meta': {'app_label': "'core'"},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'publishable': ('models.ForeignKey', ['Publishable'], {'verbose_name': "_('Publishable')"}),
            'related_ct': ('models.ForeignKey', ['ContentType'], {'verbose_name': "_('Content type')"}),
            'related_id': ('models.IntegerField', ["_('Object ID')"], {})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'db_table': "'django_site'"},
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
        'core.publishable': {
            'Meta': {'app_label': "'core'"},
            'authors': ('models.ManyToManyField', ['Author'], {'verbose_name': "_('Authors')"}),
            'category': ('models.ForeignKey', ['Category'], {'verbose_name': "_('Category')"}),
            'content_type': ('models.ForeignKey', ['ContentType'], {}),
            'description': ('models.TextField', ["_('Description')"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'photo': ('models.ForeignKey', ['Photo'], {'null': 'True', 'verbose_name': "_('Photo')", 'blank': 'True'}),
            'publish_from': ('models.DateTimeField', ["_('Publish from')"], {'default': 'PUBLISH_FROM_WHEN_EMPTY', 'editable': 'False'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'source': ('models.ForeignKey', ['Source'], {'null': 'True', 'verbose_name': "_('Source')", 'blank': 'True'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '255'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.source': {
            'Meta': {'app_label': "'core'"},
            'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ["_('Name')"], {'max_length': '200'}),
            'url': ('models.URLField', ["_('URL')"], {'blank': 'True'})
        },
        'core.dependency': {
            'Meta': {'ordering': "('dependent_ct','dependent_id',)", 'app_label': "'core'"},
            'dependent_ct': ('models.ForeignKey', ['ContentType'], {'related_name': "'depends_on_set'"}),
            'dependent_id': ('models.IntegerField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'target_ct': ('models.ForeignKey', ['ContentType'], {'related_name': "'dependency_for_set'"}),
            'target_id': ('models.IntegerField', [], {})
        },
        'core.author': {
            'Meta': {'app_label': "'core'"},
            'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
            'email': ('models.EmailField', ["_('Email')"], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ["_('Name')"], {'max_length': '200', 'blank': 'True'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'unique': 'True', 'max_length': '255'}),
            'text': ('models.TextField', ["_('Text')"], {'blank': 'True'}),
            'user': ('models.ForeignKey', ['User'], {'null': 'True', 'verbose_name': "_('User')", 'blank': 'True'})
        }
    }
    
    complete_apps = ['core']
