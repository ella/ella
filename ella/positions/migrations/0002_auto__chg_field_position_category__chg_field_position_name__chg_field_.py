# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Position.category'
        db.alter_column('positions_position', 'category_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Category']))

        # Changing field 'Position.name'
        db.alter_column('positions_position', 'name', self.gf('django.db.models.fields.CharField')(max_length=200))

        # Changing field 'Position.text'
        db.alter_column('positions_position', 'text', self.gf('django.db.models.fields.TextField')())

        # Changing field 'Position.active_till'
        db.alter_column('positions_position', 'active_till', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Changing field 'Position.target_id'
        db.alter_column('positions_position', 'target_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True))

        # Changing field 'Position.box_type'
        db.alter_column('positions_position', 'box_type', self.gf('django.db.models.fields.CharField')(max_length=200))

        # Changing field 'Position.disabled'
        db.alter_column('positions_position', 'disabled', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Position.active_from'
        db.alter_column('positions_position', 'active_from', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Changing field 'Position.target_ct'
        db.alter_column('positions_position', 'target_ct_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True))

    def backwards(self, orm):

        # Changing field 'Position.category'
        db.alter_column('positions_position', 'category_id', self.gf('models.ForeignKey')(orm['core.Category']))

        # Changing field 'Position.name'
        db.alter_column('positions_position', 'name', self.gf('models.CharField')(_('Name'), max_length=200))

        # Changing field 'Position.text'
        db.alter_column('positions_position', 'text', self.gf('models.TextField')(_('Definition')))

        # Changing field 'Position.active_till'
        db.alter_column('positions_position', 'active_till', self.gf('models.DateTimeField')(_('Position active till'), null=True))

        # Changing field 'Position.target_id'
        db.alter_column('positions_position', 'target_id', self.gf('models.PositiveIntegerField')(_('Target id'), null=True))

        # Changing field 'Position.box_type'
        db.alter_column('positions_position', 'box_type', self.gf('models.CharField')(_('Box type'), max_length=200))

        # Changing field 'Position.disabled'
        db.alter_column('positions_position', 'disabled', self.gf('models.BooleanField')(_('Disabled')))

        # Changing field 'Position.active_from'
        db.alter_column('positions_position', 'active_from', self.gf('models.DateTimeField')(_('Position active from'), null=True))

        # Changing field 'Position.target_ct'
        db.alter_column('positions_position', 'target_ct_id', self.gf('models.ForeignKey')(orm['contenttypes.ContentType'], null=True))

    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.category': {
            'Meta': {'unique_together': "(('site', 'tree_path'),)", 'object_name': 'Category'},
            'app_data': ('app_data.fields.AppDataField', [], {'default': "'{}'"}),
            'content': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'template': ('django.db.models.fields.CharField', [], {'default': "'category.html'", 'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'tree_parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Category']", 'null': 'True', 'blank': 'True'}),
            'tree_path': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'positions.position': {
            'Meta': {'object_name': 'Position'},
            'active_from': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'active_till': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'box_type': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Category']"}),
            'disabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'target_ct': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'target_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['positions']