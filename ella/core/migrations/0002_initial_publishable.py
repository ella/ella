# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    depends_on = (
        ('photos', '0001_initial'),
    )

    def forwards(self, orm):
        # Adding model 'Publishable'
        db.create_table('core_publishable', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Category'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, db_index=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Source'], null=True, blank=True)),
            ('photo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['photos.Photo'], null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('publish_from', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(3000, 1, 1, 0, 0, 0, 2), db_index=True)),
        ))
        db.send_create_signal('core', ['Publishable'])

        # Adding M2M table for field authors on 'Publishable'
        db.create_table('core_publishable_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('publishable', models.ForeignKey(orm['core.publishable'], null=False)),
            ('author', models.ForeignKey(orm['core.author'], null=False))
        ))
        db.create_unique('core_publishable_authors', ['publishable_id', 'author_id'])

        # Adding model 'Placement'
        db.create_table('core_placement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('publishable', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Publishable'])),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Category'])),
            ('publish_from', self.gf('django.db.models.fields.DateTimeField')()),
            ('publish_to', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=255, blank=True)),
            ('static', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('core', ['Placement'])

        # Adding unique constraint on 'Placement', fields ['publishable', 'category']
        db.create_unique('core_placement', ['publishable_id', 'category_id'])

        # Adding model 'Listing'
        db.create_table('core_listing', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('placement', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Placement'])),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Category'])),
            ('publish_from', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('publish_to', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('priority_from', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('priority_to', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('priority_value', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('commercial', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('core', ['Listing'])

        # Adding model 'HitCount'
        db.create_table('core_hitcount', (
            ('placement', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Placement'], primary_key=True)),
            ('last_seen', self.gf('django.db.models.fields.DateTimeField')()),
            ('hits', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
        ))
        db.send_create_signal('core', ['HitCount'])

        # Adding model 'Related'
        db.create_table('core_related', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('publishable', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Publishable'])),
            ('related_ct', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('related_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('core', ['Related'])



    def backwards(self, orm):
        # Removing unique constraint on 'Placement', fields ['publishable', 'category']
        db.delete_unique('core_placement', ['publishable_id', 'category_id'])

        # Deleting model 'Publishable'
        db.delete_table('core_publishable')

        # Removing M2M table for field authors on 'Publishable'
        db.delete_table('core_publishable_authors')

        # Deleting model 'Placement'
        db.delete_table('core_placement')

        # Deleting model 'Listing'
        db.delete_table('core_listing')

        # Deleting model 'HitCount'
        db.delete_table('core_hitcount')

        # Deleting model 'Related'
        db.delete_table('core_related')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.author': {
            'Meta': {'object_name': 'Author'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'core.category': {
            'Meta': {'ordering': "('site__name', 'tree_path')", 'unique_together': "(('site', 'tree_path'),)", 'object_name': 'Category'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'tree_parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Category']", 'null': 'True', 'blank': 'True'}),
            'tree_path': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'core.dependency': {
            'Meta': {'ordering': "('dependent_ct', 'dependent_id')", 'object_name': 'Dependency'},
            'dependent_ct': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'depends_on_set'", 'to': "orm['contenttypes.ContentType']"}),
            'dependent_id': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'target_ct': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dependency_for_set'", 'to': "orm['contenttypes.ContentType']"}),
            'target_id': ('django.db.models.fields.IntegerField', [], {})
        },
        'core.hitcount': {
            'Meta': {'object_name': 'HitCount'},
            'hits': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {}),
            'placement': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Placement']", 'primary_key': 'True'})
        },
        'core.listing': {
            'Meta': {'ordering': "('-publish_from',)", 'object_name': 'Listing'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Category']"}),
            'commercial': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'placement': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Placement']"}),
            'priority_from': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'priority_to': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'priority_value': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'publish_from': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'publish_to': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'core.placement': {
            'Meta': {'unique_together': "(('publishable', 'category'),)", 'object_name': 'Placement'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Category']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'publish_from': ('django.db.models.fields.DateTimeField', [], {}),
            'publish_to': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'publishable': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Publishable']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'static': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'core.publishable': {
            'Meta': {'object_name': 'Publishable'},
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Author']", 'symmetrical': 'False'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Category']"}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'photo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['photos.Photo']", 'null': 'True', 'blank': 'True'}),
            'publish_from': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(3000, 1, 1, 0, 0, 0, 2)', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Source']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'core.related': {
            'Meta': {'object_name': 'Related'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'publishable': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Publishable']"}),
            'related_ct': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'related_id': ('django.db.models.fields.IntegerField', [], {})
        },
        'core.source': {
            'Meta': {'object_name': 'Source'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'photos.photo': {
            'Meta': {'ordering': "('-created',)", 'object_name': 'Photo'},
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'photo_set'", 'symmetrical': 'False', 'to': "orm['core.Author']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'height': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'important_bottom': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'important_left': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'important_right': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'important_top': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Source']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['core']

