
from south.db import db
from django.db import models
from ella.ellatagging.models import *

class Migration:
    
    def forwards(self, orm):
        # dropping abandoned columns
        db.delete_column('tagging_taggeditem', 'category_id')
        db.delete_column('tagging_taggeditem', 'priority')
    
    def backwards(self, orm):
        # adding old columns
        db.add_column('tagging_taggeditem', 'category', models.ForeignKey(orm['core.Category'], null=True, editable=False))
        db.add_column('tagging_taggeditem', 'priority', models.IntegerField(db_index=True))

        # Deleting unique_together for [tag, content_type, object_id] on TaggedItem.
        db.delete_unique('tagging_taggeditem', ['tag_id', 'content_type_id', 'object_id'])

        # Creating unique_together for [tag, content_type, object_id, priority] on TaggedItem.
        db.create_unique('tagging_taggeditem', ['tag_id', 'content_type_id', 'object_id', 'priority'])
    
    
    models = {
        'core.category': {
            'Meta': {'ordering': "('site','tree_path',)", 'unique_together': "(('site','tree_path'),)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'tagging.taggeditem': {
            'Meta': {'unique_together': "(('tag','content_type','object_id','priority'),)"},
            'category': ('models.ForeignKey', ["orm['core.Category']"], {'null': 'True', 'editable': 'False'}),
            'content_type': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'verbose_name': "_('content type')"}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('models.PositiveIntegerField', ["_('object id')"], {'db_index': 'True'}),
            'priority': ('models.IntegerField', [], {'db_index': 'True'}),
            'tag': ('models.ForeignKey', ["orm['tagging.Tag']"], {'related_name': "'items'", 'verbose_name': "_('tag')"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'tagging.tag': {
            'Meta': {'ordering': "('name',)"},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
        }
    }
    
    complete_apps = ['ellatagging']
