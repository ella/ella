
from south.db import db
from django.db import models
from djangobaselibrary.sample.models import *

class Migration:

    def forwards(self, orm):

        # we have to drop primary key, but it can't be AutoField
        db.alter_column('sample_spam', 'id', models.IntegerField())
        db.drop_primary_key('sample_spam')

        # Deleting field 'Spam.id'
        # TODO:
        # but we need to find any of our children
        # because they contain constraint to us
        db.delete_column('sample_spam', 'id')
        # Adding field 'Spam.id'
        db.add_column('sample_spam', 'id', models.AutoField(primary_key=True))


    def backwards(self, orm):
        pass


    models = {
        'sample.employee': {
            'Meta': {'ordering': "('last_name','first_name')"},
            'employee_code': ('models.CharField', [], {'max_length': '10', 'primary_key': 'True', 'db_column': "'code'"}),
            'first_name': ('models.CharField', [], {'max_length': '20'}),
            'last_name': ('models.CharField', [], {'max_length': '20'})
        },
        'sample.spam': {
            'Meta': {'unique_together': "(('name','expires'),)"},
            'count': ('models.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'expires': ('models.DateTimeField', [], {}),
            'name': ('models.CharField', [], {'max_length': '255'}),
            'primarykey': ('models.IntegerField', [], {'primary_key': 'True', 'db_column': "'primarykey'"}),
            'type': ('models.IntegerField', [], {}),
            'weight': ('models.FloatField', [], {})
        },
        'sample.business': {
            'employees': ('models.ManyToManyField', ["orm['sample.Employee']"], {}),
            'name': ('models.CharField', [], {'max_length': '20', 'primary_key': 'True'})
        },
        'sample.type': {
            'description': ('models.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['sample']
