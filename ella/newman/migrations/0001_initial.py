
from south.db import db
from django.db import models
from ella.newman.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'DevMessage'
        db.create_table('newman_devmessage', (
            ('id', orm['newman.DevMessage:id']),
            ('title', orm['newman.DevMessage:title']),
            ('slug', orm['newman.DevMessage:slug']),
            ('summary', orm['newman.DevMessage:summary']),
            ('details', orm['newman.DevMessage:details']),
            ('version', orm['newman.DevMessage:version']),
            ('author', orm['newman.DevMessage:author']),
            ('ts', orm['newman.DevMessage:ts']),
        ))
        db.send_create_signal('newman', ['DevMessage'])
        
        # Adding model 'AdminSetting'
        db.create_table('newman_adminsetting', (
            ('id', orm['newman.AdminSetting:id']),
            ('user', orm['newman.AdminSetting:user']),
            ('group', orm['newman.AdminSetting:group']),
            ('var', orm['newman.AdminSetting:var']),
            ('val', orm['newman.AdminSetting:val']),
        ))
        db.send_create_signal('newman', ['AdminSetting'])
        
        # Adding model 'AdminUserDraft'
        db.create_table('newman_adminuserdraft', (
            ('id', orm['newman.AdminUserDraft:id']),
            ('ct', orm['newman.AdminUserDraft:ct']),
            ('user', orm['newman.AdminUserDraft:user']),
            ('data', orm['newman.AdminUserDraft:data']),
            ('title', orm['newman.AdminUserDraft:title']),
            ('ts', orm['newman.AdminUserDraft:ts']),
        ))
        db.send_create_signal('newman', ['AdminUserDraft'])
        
        # Adding model 'DenormalizedCategoryUserRole'
        db.create_table('newman_denormalizedcategoryuserrole', (
            ('id', orm['newman.DenormalizedCategoryUserRole:id']),
            ('user_id', orm['newman.DenormalizedCategoryUserRole:user_id']),
            ('permission_id', orm['newman.DenormalizedCategoryUserRole:permission_id']),
            ('permission_codename', orm['newman.DenormalizedCategoryUserRole:permission_codename']),
            ('category_id', orm['newman.DenormalizedCategoryUserRole:category_id']),
            ('root_category_id', orm['newman.DenormalizedCategoryUserRole:root_category_id']),
            ('contenttype_id', orm['newman.DenormalizedCategoryUserRole:contenttype_id']),
        ))
        db.send_create_signal('newman', ['DenormalizedCategoryUserRole'])
        
        # Adding model 'AdminHelpItem'
        db.create_table('newman_adminhelpitem', (
            ('id', orm['newman.AdminHelpItem:id']),
            ('ct', orm['newman.AdminHelpItem:ct']),
            ('field', orm['newman.AdminHelpItem:field']),
            ('lang', orm['newman.AdminHelpItem:lang']),
            ('short', orm['newman.AdminHelpItem:short']),
            ('long', orm['newman.AdminHelpItem:long']),
        ))
        db.send_create_signal('newman', ['AdminHelpItem'])
        
        # Adding model 'CategoryUserRole'
        db.create_table('newman_categoryuserrole', (
            ('id', orm['newman.CategoryUserRole:id']),
            ('user', orm['newman.CategoryUserRole:user']),
            ('group', orm['newman.CategoryUserRole:group']),
        ))
        db.send_create_signal('newman', ['CategoryUserRole'])
        
        # Adding ManyToManyField 'CategoryUserRole.category'
        db.create_table('newman_categoryuserrole_category', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('categoryuserrole', models.ForeignKey(orm.CategoryUserRole, null=False)),
            ('category', models.ForeignKey(orm['core.Category'], null=False))
        ))
        
        # Creating unique_together for [user, var] on AdminSetting.
        db.create_unique('newman_adminsetting', ['user_id', 'var'])
        
        # Creating unique_together for [slug, ts] on DevMessage.
        db.create_unique('newman_devmessage', ['slug', 'ts'])
        
        # Creating unique_together for [user_id, permission_codename, permission_id, category_id, contenttype_id] on DenormalizedCategoryUserRole.
        db.create_unique('newman_denormalizedcategoryuserrole', ['user_id', 'permission_codename', 'permission_id', 'category_id', 'contenttype_id'])
        
        # Creating unique_together for [group, var] on AdminSetting.
        db.create_unique('newman_adminsetting', ['group_id', 'var'])
        
        # Creating unique_together for [ct, field, lang] on AdminHelpItem.
        db.create_unique('newman_adminhelpitem', ['ct_id', 'field', 'lang'])
        
    
    
    def backwards(self, orm):
        
        # Deleting unique_together for [ct, field, lang] on AdminHelpItem.
        db.delete_unique('newman_adminhelpitem', ['ct_id', 'field', 'lang'])
        
        # Deleting unique_together for [group, var] on AdminSetting.
        db.delete_unique('newman_adminsetting', ['group_id', 'var'])
        
        # Deleting unique_together for [user_id, permission_codename, permission_id, category_id, contenttype_id] on DenormalizedCategoryUserRole.
        db.delete_unique('newman_denormalizedcategoryuserrole', ['user_id', 'permission_codename', 'permission_id', 'category_id', 'contenttype_id'])
        
        # Deleting unique_together for [slug, ts] on DevMessage.
        db.delete_unique('newman_devmessage', ['slug', 'ts'])
        
        # Deleting unique_together for [user, var] on AdminSetting.
        db.delete_unique('newman_adminsetting', ['user_id', 'var'])
        
        # Deleting model 'DevMessage'
        db.delete_table('newman_devmessage')
        
        # Deleting model 'AdminSetting'
        db.delete_table('newman_adminsetting')
        
        # Deleting model 'AdminUserDraft'
        db.delete_table('newman_adminuserdraft')
        
        # Deleting model 'DenormalizedCategoryUserRole'
        db.delete_table('newman_denormalizedcategoryuserrole')
        
        # Deleting model 'AdminHelpItem'
        db.delete_table('newman_adminhelpitem')
        
        # Deleting model 'CategoryUserRole'
        db.delete_table('newman_categoryuserrole')
        
        # Dropping ManyToManyField 'CategoryUserRole.category'
        db.delete_table('newman_categoryuserrole_category')
        
    
    
    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.category': {
            'Meta': {'unique_together': "(('site', 'tree_path'),)"},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'tree_parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Category']", 'null': 'True', 'blank': 'True'}),
            'tree_path': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'newman.adminhelpitem': {
            'Meta': {'unique_together': "(('ct', 'field', 'lang'),)"},
            'ct': ('CachedForeignKey', ["orm['contenttypes.ContentType']"], {}),
            'field': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lang': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'long': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'short': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'newman.adminsetting': {
            'Meta': {'unique_together': "(('user', 'var'), ('group', 'var'))"},
            'group': ('CachedForeignKey', ["orm['auth.Group']"], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('CachedForeignKey', ["orm['auth.User']"], {'null': 'True', 'blank': 'True'}),
            'val': ('django.db.models.fields.TextField', [], {}),
            'var': ('django.db.models.fields.SlugField', [], {'max_length': '64', 'db_index': 'True'})
        },
        'newman.adminuserdraft': {
            'ct': ('CachedForeignKey', ["orm['contenttypes.ContentType']"], {}),
            'data': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'ts': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('CachedForeignKey', ["orm['auth.User']"], {})
        },
        'newman.categoryuserrole': {
            'category': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Category']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'newman.denormalizedcategoryuserrole': {
            'Meta': {'unique_together': "(('user_id', 'permission_codename', 'permission_id', 'category_id', 'contenttype_id'),)"},
            'category_id': ('django.db.models.fields.IntegerField', [], {}),
            'contenttype_id': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission_codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'permission_id': ('django.db.models.fields.IntegerField', [], {}),
            'root_category_id': ('django.db.models.fields.IntegerField', [], {}),
            'user_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'})
        },
        'newman.devmessage': {
            'Meta': {'unique_together': "(('slug', 'ts'),)"},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'details': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '32', 'db_index': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ts': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'sites.site': {
            'Meta': {'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }
    
    complete_apps = ['newman']
