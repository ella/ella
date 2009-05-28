
from south.db import db
from django.db import models
from djangobaselibrary.sample.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Employee'
        db.create_table('sample_employee', (
            ('employee_code', models.CharField(max_length=10, primary_key=True, db_column='code')),
            ('first_name', models.CharField(max_length=20)),
            ('last_name', models.CharField(max_length=20)),
        ))
        db.send_create_signal('sample', ['Employee'])
        
        # Adding model 'Business'
        db.create_table('sample_business', (
            ('name', models.CharField(max_length=20, primary_key=True)),
        ))
        db.send_create_signal('sample', ['Business'])
        
        # Adding ManyToManyField 'Business.employees'
        db.create_table('sample_business_employees', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('business', models.ForeignKey(orm.Business, null=False)),
            ('employee', models.ForeignKey(orm.Employee, null=False))
        ))
        
    
    
    def backwards(self, orm):
        
        # Dropping ManyToManyField 'Business.employees'
        db.delete_table('sample_business_employees')
        
        # Deleting model 'Employee'
        db.delete_table('sample_employee')
        
        # Deleting model 'Business'
        db.delete_table('sample_business')
        
    
    
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
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '255'}),
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
