
from south.db import db
from django.db import models
from south.v2 import SchemaMigration

class Migration(SchemaMigration):

    def forwards(self, orm):
        db.alter_column('core_placement', 'publishable_id', models.ForeignKey(orm['core.Publishable'], null=False))
        db.create_index('core_placement', ['publishable_id'])

        db.delete_unique('core_placement', ('target_ct_id', 'target_id', 'category_id'))
        db.delete_column('core_placement', 'target_ct_id')
        db.delete_column('core_placement', 'target_id')

    def backwards(self, orm):
        db.add_column('core_placement', 'target_ct', models.ForeignKey(orm['contenttypes.ContentType'], null=True))
        db.add_column('core_placement', 'target_id', models.IntegerField(null=True))

        db.drop_index('core_placement', ['publishable_id'])
        db.alter_column('core_placement', 'publishable_id', models.IntegerField(null=True))


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.publishable': {
            'Meta': {'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
    }

