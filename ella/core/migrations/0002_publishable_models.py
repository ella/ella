
from south.db import db
from django.db import models
from ella.core.models import *

class Migration:

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
            ('description', models.TextField(_('Description'))),
            ('publish_from', models.DateTimeField(_('Publish from'), default=datetime(3000, 1, 1, 0, 0), editable=False)),
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
    }

