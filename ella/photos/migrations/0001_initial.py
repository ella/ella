# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    depends_on = (
        ('core', '0001_initial'),
    )


    def forwards(self, orm):
        
        # Adding model 'Photo'
        db.create_table('photos_photo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, db_index=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('width', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('height', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('important_top', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('important_left', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('important_bottom', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('important_right', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Source'], null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('photos', ['Photo'])

        # Adding M2M table for field authors on 'Photo'
        db.create_table('photos_photo_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('photo', models.ForeignKey(orm['photos.photo'], null=False)),
            ('author', models.ForeignKey(orm['core.author'], null=False))
        ))
        db.create_unique('photos_photo_authors', ['photo_id', 'author_id'])

        # Adding model 'Format'
        db.create_table('photos_format', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('max_width', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('max_height', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('flexible_height', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('flexible_max_height', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('stretch', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('nocrop', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('resample_quality', self.gf('django.db.models.fields.IntegerField')(default=85)),
        ))
        db.send_create_signal('photos', ['Format'])

        # Adding M2M table for field sites on 'Format'
        db.create_table('photos_format_sites', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('format', models.ForeignKey(orm['photos.format'], null=False)),
            ('site', models.ForeignKey(orm['sites.site'], null=False))
        ))
        db.create_unique('photos_format_sites', ['format_id', 'site_id'])

        # Adding model 'FormatedPhoto'
        db.create_table('photos_formatedphoto', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('photo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['photos.Photo'])),
            ('format', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['photos.Format'])),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=300)),
            ('crop_left', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('crop_top', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('crop_width', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('crop_height', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('width', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('height', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('photos', ['FormatedPhoto'])

        # Adding unique constraint on 'FormatedPhoto', fields ['photo', 'format']
        db.create_unique('photos_formatedphoto', ['photo_id', 'format_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'FormatedPhoto', fields ['photo', 'format']
        db.delete_unique('photos_formatedphoto', ['photo_id', 'format_id'])

        # Deleting model 'Photo'
        db.delete_table('photos_photo')

        # Removing M2M table for field authors on 'Photo'
        db.delete_table('photos_photo_authors')

        # Deleting model 'Format'
        db.delete_table('photos_format')

        # Removing M2M table for field sites on 'Format'
        db.delete_table('photos_format_sites')

        # Deleting model 'FormatedPhoto'
        db.delete_table('photos_formatedphoto')


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
        'core.source': {
            'Meta': {'object_name': 'Source'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'photos.format': {
            'Meta': {'ordering': "('name', '-max_width')", 'object_name': 'Format'},
            'flexible_height': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'flexible_max_height': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_height': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'max_width': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'nocrop': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'resample_quality': ('django.db.models.fields.IntegerField', [], {'default': '85'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sites.Site']", 'symmetrical': 'False'}),
            'stretch': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'photos.formatedphoto': {
            'Meta': {'unique_together': "(('photo', 'format'),)", 'object_name': 'FormatedPhoto'},
            'crop_height': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'crop_left': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'crop_top': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'crop_width': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'format': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['photos.Format']"}),
            'height': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '300'}),
            'photo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['photos.Photo']"}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {})
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

    complete_apps = ['photos']
