
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

    def ___forwards(self, orm):

        # Adding field 'Related.related_ct'
        db.add_column('core_related', 'related_ct', models.ForeignKey(orm['contenttypes.ContentType'], verbose_name=_('Content type')))
        # Adding field 'Related.related_id'
        db.add_column('core_related', 'related_id', models.IntegerField(_('Object ID')))
        # Adding field 'Related.publishable'
        db.add_column('core_related', 'publishable', models.ForeignKey(orm.Publishable, verbose_name=_('Publishable')))
        # Deleting field 'Related.target_ct'
        db.delete_column('core_related', 'target_ct_id')
        # Deleting field 'Related.source_id'
        db.delete_column('core_related', 'source_id')
        # Deleting field 'Related.target_id'
        db.delete_column('core_related', 'target_id')
        # Deleting field 'Related.source_ct'
        db.delete_column('core_related', 'source_ct_id')

        # Adding field 'Placement.publishable'
        db.add_column('core_placement', 'publishable', models.ForeignKey(orm.Publishable, verbose_name=_('Publishable object')))
        # Deleting field 'Placement.target_id'
        db.delete_column('core_placement', 'target_id')
        # Deleting field 'Placement.target_ct'
        db.delete_column('core_placement', 'target_ct_id')
        # Changing field 'Placement.category'
        db.alter_column('core_placement', 'category_id', models.ForeignKey(orm['core.Category'], verbose_name=_('Category'), db_index=True))
        # Changing field 'Placement.static'
        db.alter_column('core_placement', 'static', models.BooleanField(_('static'), default=False))

        # Adding field 'Listing.publish_to'
        db.add_column('core_listing', 'publish_to', models.DateTimeField(_("End of listing"), null=True, blank=True))
        # Deleting field 'Listing.remove'
        db.delete_column('core_listing', 'remove')
        # Changing field 'Listing.category'
        db.alter_column('core_listing', 'category_id', models.ForeignKey(orm['core.Category'], verbose_name=_('Category'), db_index=True))
        # Changing field 'Listing.placement'
        db.alter_column('core_listing', 'placement_id', models.ForeignKey(orm['core.Placement'], verbose_name=_('Placement')))

        # Adding field 'Author.email'
        db.add_column('core_author', 'email', models.EmailField(_('Email'), blank=True))
        # Changing field 'Author.user'
        db.alter_column('core_author', 'user_id', models.ForeignKey(orm['auth.User'], null=True, verbose_name=_('User'), blank=True))


    def ___backwards(self, orm):

        # Deleting field 'Author.email'
        db.delete_column('core_author', 'email')
        # Changing field 'Author.user'
        db.alter_column('core_author', 'user_id', models.ForeignKey(orm['auth.User'], null=True, blank=True))

        # Deleting field 'Listing.publish_to'
        db.delete_column('core_listing', 'publish_to')
        # Adding field 'Listing.remove'
        db.add_column('core_listing', 'remove', models.BooleanField(_("Remove"), default=False))
        # Changing field 'Listing.category'
        db.alter_column('core_listing', 'category_id', models.ForeignKey(orm['core.Category'], db_index=True))
        # Changing field 'Listing.placement'
        db.alter_column('core_listing', 'placement_id', models.ForeignKey(orm['core.Placement']))

        # Deleting field 'Placement.publishable'
        db.delete_column('core_placement', 'publishable_id')
        # Adding field 'Placement.target_id'
        db.add_column('core_placement', 'target_id', models.IntegerField())
        # Adding field 'Placement.target_ct'
        db.add_column('core_placement', 'target_ct', models.ForeignKey(orm['contenttypes.ContentType']))
        # Changing field 'Placement.category'
        db.alter_column('core_placement', 'category_id', models.ForeignKey(orm['core.Category'], db_index=True))
        # Changing field 'Placement.static'
        db.alter_column('core_placement', 'static', models.BooleanField(default=False))

        # Deleting field 'Related.related_ct'
        db.delete_column('core_related', 'related_ct_id')
        # Deleting field 'Related.related_id'
        db.delete_column('core_related', 'related_id')
        # Deleting field 'Related.publishable'
        db.delete_column('core_related', 'publishable_id')
        # Adding field 'Related.target_ct'
        db.add_column('core_related', 'target_ct', models.ForeignKey(orm['contenttypes.ContentType'], related_name='relation_for_set'))
        # Adding field 'Related.source_id'
        db.add_column('core_related', 'source_id', models.IntegerField())
        # Adding field 'Related.target_id'
        db.add_column('core_related', 'target_id', models.IntegerField())
        # Adding field 'Related.source_ct'
        db.add_column('core_related', 'source_ct', models.ForeignKey(orm['contenttypes.ContentType'], related_name='related_on_set'))

    def backwards(self, orm):

        # Dropping ManyToManyField 'Publishable.authors'
        db.delete_table('core_publishable_authors')

        # Deleting model 'Dependency'
        db.delete_table('core_dependency')

        # Deleting model 'Publishable'
        db.delete_table('core_publishable')


    models = {
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
        'core.placement': {
            'Meta': {'app_label': "'core'"},
            'category': ('models.ForeignKey', ["orm['core.Category']"], {'verbose_name': "_('Category')", 'db_index': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'publish_from': ('models.DateTimeField', ['_("Start of visibility")'], {}),
            'publish_to': ('models.DateTimeField', ['_("End of visibility")'], {'null': 'True', 'blank': 'True'}),
            'publishable': ('models.ForeignKey', ["orm['core.Publishable']"], {'verbose_name': "_('Publishable object')"}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255', 'blank': 'True'}),
            'static': ('models.BooleanField', ["_('static')"], {'default': 'False'})
        },
        'core.listing': {
            'Meta': {'ordering': "('-publish_from',)", 'app_label': "'core'"},
            'category': ('models.ForeignKey', ["orm['core.Category']"], {'verbose_name': "_('Category')", 'db_index': 'True'}),
            'commercial': ('models.BooleanField', ['_("Commercial")'], {'default': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'placement': ('models.ForeignKey', ["orm['core.Placement']"], {'verbose_name': "_('Placement')"}),
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
            'placement': ('models.ForeignKey', ["orm['core.Placement']"], {'primary_key': 'True'})
        },
        'core.related': {
            'Meta': {'app_label': "'core'"},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'publishable': ('models.ForeignKey', ["orm['core.Publishable']"], {'verbose_name': "_('Publishable')"}),
            'related_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'verbose_name': "_('Content type')"}),
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
            'authors': ('models.ManyToManyField', ["orm['core.Author']"], {'verbose_name': "_('Authors')"}),
            'category': ('models.ForeignKey', ["orm['core.Category']"], {'verbose_name': "_('Category')"}),
            'comments': '<< PUT FIELD DEFINITION HERE >>',
            'content_type': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {}),
            'description': ('models.TextField', ["_('Description')"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'photo': ('models.ForeignKey', ["orm['photos.Photo']"], {'null': 'True', 'verbose_name': "_('Photo')", 'blank': 'True'}),
            'publish_from': ('models.DateTimeField', ["_('Publish from')"], {'default': 'datetime.datetime(3000, 1, 1, 0, 0)', 'editable': 'False'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'source': ('models.ForeignKey', ["orm['core.Source']"], {'null': 'True', 'verbose_name': "_('Source')", 'blank': 'True'}),
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
            'dependent_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'related_name': "'depends_on_set'"}),
            'dependent_id': ('models.IntegerField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'target_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'related_name': "'dependency_for_set'"}),
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
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'null': 'True', 'verbose_name': "_('User')", 'blank': 'True'})
        }
    }

    complete_apps = ['core']
