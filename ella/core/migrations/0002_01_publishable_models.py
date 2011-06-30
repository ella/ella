
from south.db import db
from django.db import models
from ella.core.models import *
import datetime

class Migration:

    depends_on = (
        ('photos', '0001_initial'),
    )

    def forwards(self, orm):

        # Adding model 'Publishable'
        db.create_table('core_publishable', (
            ('id', models.AutoField(primary_key=True)),
            ('content_type', models.ForeignKey(orm['contenttypes.ContentType'])),
            ('category', models.ForeignKey(orm.Category, verbose_name=_('Category'))),
            ('title', models.CharField(_('Title'), max_length=255)),
            ('slug', models.SlugField(_('Slug'), max_length=255)),
            ('source', models.ForeignKey(orm.Source, null=True, verbose_name=_('Source'), blank=True)),
            ('photo', models.ForeignKey(orm['photos.Photo'], null=True, verbose_name=_('Photo'), blank=True)),
            ('description', models.TextField(_('Description'), null=True, blank=True)),
            ('publish_from', models.DateTimeField(_('Publish from'), default=datetime.datetime(3000, 1, 1, 0, 0), editable=False)),
        ))
        db.send_create_signal('core', ['Publishable'])

        # Adding model 'Dependency'
        db.create_table('core_dependency', (
            ('id', models.AutoField(primary_key=True)),
            ('target_ct', models.ForeignKey(orm['contenttypes.ContentType'], related_name='dependency_for_set')),
            ('target_id', models.IntegerField()),
            ('dependent_ct', models.ForeignKey(orm['contenttypes.ContentType'], related_name='depends_on_set')),
            ('dependent_id', models.IntegerField()),
        ))
        db.send_create_signal('core', ['Dependency'])

        # Adding ManyToManyField 'Publishable.authors'
        db.create_table('core_publishable_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('publishable', models.ForeignKey(orm.Publishable, null=False)),
            ('author', models.ForeignKey(orm.Author, null=False))
        ))

    def backwards(self, orm):

        # Dropping ManyToManyField 'Publishable.authors'
        db.delete_table('core_publishable_authors')

        # Deleting model 'Dependency'
        db.delete_table('core_dependency')

        # Deleting model 'Publishable'
        db.delete_table('core_publishable')


    models = {
        # orm.Category
        'core.category': {
            'Meta': {'unique_together': "(('site','tree_path'),)", 'app_label': "'core'"},
            'description': ('models.TextField', ['_("Category Description")'], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'site': ('models.ForeignKey', ["orm['sites.Site']"], {}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'title': ('models.CharField', ['_("Category Title")'], {'max_length': '200'}),
            'tree_parent': ('models.ForeignKey', ["orm['core.Category']"], {'null': 'True', 'verbose_name': '_("Parent Category")', 'blank': 'True'}),
            'tree_path': ('models.CharField', [], {'editable': 'False', 'max_length': '255', 'verbose_name': '_("Path from root category")'})
        },
        # orm['sites.Site']
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'db_table': "'django_site'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        # orm['photos.Photo']
        'photos.photo': {
            'Meta': {'ordering': "('-created',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        # orm.Publishable
        'core.publishable': {
            'Meta': {'app_label': "'core'"},
            'authors': ('models.ManyToManyField', ["orm['core.Author']"], {'verbose_name': "_('Authors')"}),
            'category': ('models.ForeignKey', ["orm['core.Category']"], {'verbose_name': "_('Category')"}),
            'content_type': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {}),
            'description': ('models.TextField', ["_('Description')"], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'photo': ('models.ForeignKey', ["orm['photos.Photo']"], {'null': 'True', 'verbose_name': "_('Photo')", 'blank': 'True'}),
            'publish_from': ('models.DateTimeField', ["_('Publish from')"], {'default': 'datetime.datetime(3000, 1, 1, 0, 0)', 'editable': 'False'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'source': ('models.ForeignKey', ["orm['core.Source']"], {'null': 'True', 'verbose_name': "_('Source')", 'blank': 'True'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '255'})
        },
        # orm['contenttypes.ContentType']
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        # orm.Source
        'core.source': {
            'Meta': {'app_label': "'core'"},
            'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ["_('Name')"], {'max_length': '200'}),
            'url': ('models.URLField', ["_('URL')"], {'blank': 'True'})
        },
        # orm.Author
        'core.author': {
            'Meta': {'app_label': "'core'"},
            'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
            'email': ('models.EmailField', ["_('Email')"], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ["_('Name')"], {'max_length': '200', 'blank': 'True'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'unique': 'True', 'max_length': '255'}),
            'text': ('models.TextField', ["_('Text')"], {'blank': 'True'}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'null': 'True', 'verbose_name': "_('User')", 'blank': 'True'})
        },
        # orm['auth.User']
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
    }

