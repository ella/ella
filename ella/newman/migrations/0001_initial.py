
from south.db import db
from django.db import models
from ella.newman.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'DevMessage'
        db.create_table('newman_devmessage', (
            ('id', models.AutoField(primary_key=True)),
            ('title', models.CharField(_('Title'), max_length=255)),
            ('slug', models.SlugField(_('Slug'), max_length=32)),
            ('summary', models.TextField(_('Summary'))),
            ('details', models.TextField(_('Detail'), blank=True)),
            ('version', models.CharField(_('Version'), max_length=32)),
            ('author', models.ForeignKey(orm['auth.User'], editable=False)),
            ('ts', models.DateTimeField(auto_now_add=True, editable=False)),
        ))
        db.send_create_signal('newman', ['DevMessage'])
        
        # Adding model 'AdminSetting'
        db.create_table('newman_adminsetting', (
            ('id', models.AutoField(primary_key=True)),
            ('user', CachedForeignKey(orm['auth.User'], null=True, verbose_name=_('User'), blank=True)),
            ('group', CachedForeignKey(orm['auth.Group'], null=True, verbose_name=_('Group'), blank=True)),
            ('var', models.SlugField(_('Variable'), max_length=64)),
            ('val', models.TextField(_('Value'))),
        ))
        db.send_create_signal('newman', ['AdminSetting'])
        
        # Adding model 'AdminUserDraft'
        db.create_table('newman_adminuserdraft', (
            ('id', models.AutoField(primary_key=True)),
            ('ct', CachedForeignKey(orm['contenttypes.ContentType'], verbose_name=_('Model'))),
            ('user', CachedForeignKey(orm['auth.User'], verbose_name=_('User'))),
            ('data', models.TextField(_('Data'))),
            ('title', models.CharField(_('Title'), max_length=64, blank=True)),
            ('ts', models.DateTimeField(auto_now=True, editable=False)),
        ))
        db.send_create_signal('newman', ['AdminUserDraft'])
        
        # Adding model 'DenormalizedCategoryUserRole'
        db.create_table('newman_denormalizedcategoryuserrole', (
            ('id', models.AutoField(primary_key=True)),
            ('user_id', models.IntegerField(db_index=True)),
            ('permission_id', models.IntegerField()),
            ('permission_codename', models.CharField(max_length=100)),
            ('category_id', models.IntegerField()),
            ('root_category_id', models.IntegerField()),
            ('contenttype_id', models.IntegerField()),
        ))
        db.send_create_signal('newman', ['DenormalizedCategoryUserRole'])
        
        # Adding model 'AdminHelpItem'
        db.create_table('newman_adminhelpitem', (
            ('id', models.AutoField(primary_key=True)),
            ('ct', CachedForeignKey(orm['contenttypes.ContentType'], verbose_name=_('Model'))),
            ('field', models.CharField(_('Field'), max_length=64, blank=True)),
            ('lang', models.CharField(_('Language'), max_length=5)),
            ('short', models.CharField(_('Short help'), max_length=255)),
            ('long', models.TextField(_('Full message'), blank=True)),
        ))
        db.send_create_signal('newman', ['AdminHelpItem'])
        
        # Adding model 'CategoryUserRole'
        db.create_table('newman_categoryuserrole', (
            ('id', models.AutoField(primary_key=True)),
            ('user', models.ForeignKey(orm['auth.User'])),
            ('group', models.ForeignKey(orm['auth.Group'])),
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
        
        # Deleting unique_together for [user, var] on AdminSetting.
        db.delete_unique('newman_adminsetting', ['user_id', 'var'])
        
        # Deleting unique_together for [slug, ts] on DevMessage.
        db.delete_unique('newman_devmessage', ['slug', 'ts'])
        
        # Deleting unique_together for [user_id, permission_codename, permission_id, category_id, contenttype_id] on DenormalizedCategoryUserRole.
        db.delete_unique('newman_denormalizedcategoryuserrole', ['user_id', 'permission_codename', 'permission_id', 'category_id', 'contenttype_id'])
        
        # Deleting unique_together for [group, var] on AdminSetting.
        db.delete_unique('newman_adminsetting', ['group_id', 'var'])
        
        # Deleting unique_together for [ct, field, lang] on AdminHelpItem.
        db.delete_unique('newman_adminhelpitem', ['ct_id', 'field', 'lang'])
        
    
    
    models = {
        'core.category': {
            'Meta': {'unique_together': "(('site','tree_path'),)", 'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'newman.devmessage': {
            'Meta': {'ordering': "('-ts',)", 'unique_together': "(('slug','ts',),)"},
            'author': ('models.ForeignKey', ["orm['auth.User']"], {'editable': 'False'}),
            'details': ('models.TextField', ["_('Detail')"], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '32'}),
            'summary': ('models.TextField', ["_('Summary')"], {}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '255'}),
            'ts': ('models.DateTimeField', [], {'auto_now_add': 'True', 'editable': 'False'}),
            'version': ('models.CharField', ["_('Version')"], {'max_length': '32'})
        },
        'newman.adminsetting': {
            'Meta': {'unique_together': "(('user','var',),('group','var',),)"},
            'group': ('CachedForeignKey', ["orm['auth.Group']"], {'null': 'True', 'verbose_name': "_('Group')", 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'user': ('CachedForeignKey', ["orm['auth.User']"], {'null': 'True', 'verbose_name': "_('User')", 'blank': 'True'}),
            'val': ('models.TextField', ["_('Value')"], {}),
            'var': ('models.SlugField', ["_('Variable')"], {'max_length': '64'})
        },
        'newman.adminuserdraft': {
            'Meta': {'ordering': "('-ts',)"},
            'ct': ('CachedForeignKey', ["orm['contenttypes.ContentType']"], {'verbose_name': "_('Model')"}),
            'data': ('models.TextField', ["_('Data')"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '64', 'blank': 'True'}),
            'ts': ('models.DateTimeField', [], {'auto_now': 'True', 'editable': 'False'}),
            'user': ('CachedForeignKey', ["orm['auth.User']"], {'verbose_name': "_('User')"})
        },
        'newman.denormalizedcategoryuserrole': {
            'Meta': {'unique_together': "('user_id','permission_codename','permission_id','category_id','contenttype_id')"},
            'category_id': ('models.IntegerField', [], {}),
            'contenttype_id': ('models.IntegerField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'permission_codename': ('models.CharField', [], {'max_length': '100'}),
            'permission_id': ('models.IntegerField', [], {}),
            'root_category_id': ('models.IntegerField', [], {}),
            'user_id': ('models.IntegerField', [], {'db_index': 'True'})
        },
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'newman.adminhelpitem': {
            'Meta': {'ordering': "('ct','field',)", 'unique_together': "(('ct','field','lang',),)"},
            'ct': ('CachedForeignKey', ["orm['contenttypes.ContentType']"], {'verbose_name': "_('Model')"}),
            'field': ('models.CharField', ["_('Field')"], {'max_length': '64', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'lang': ('models.CharField', ["_('Language')"], {'max_length': '5'}),
            'long': ('models.TextField', ["_('Full message')"], {'blank': 'True'}),
            'short': ('models.CharField', ["_('Short help')"], {'max_length': '255'})
        },
        'auth.group': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'newman.categoryuserrole': {
            'category': ('models.ManyToManyField', ["orm['core.Category']"], {}),
            'group': ('models.ForeignKey', ["orm['auth.Group']"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {})
        }
    }
    
    complete_apps = ['newman']
