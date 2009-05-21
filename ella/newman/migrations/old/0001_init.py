
from south.db import db
from django.db import models
from ella.newman.models import *

class Migration:

    depends_on = (
        ("core", "0001_initial"),
    )
    
    def forwards(self, orm):
        
        # Adding model 'DevMessage'
        db.create_table('newman_devmessage', (
            ('title', models.CharField(_('Title'), max_length=255)),
            ('author', models.ForeignKey(orm['auth.User'], editable=False)),
            ('ts', models.DateTimeField(auto_now_add=True, editable=False)),
            ('summary', models.TextField(_('Summary'))),
            ('version', models.CharField(_('Version'), max_length=32)),
            ('details', models.TextField(_('Detail'), blank=True)),
            ('id', models.AutoField(primary_key=True)),
            ('slug', models.SlugField(_('Slug'), max_length=32)),
        ))
        db.send_create_signal('newman', ['DevMessage'])
        
        # Adding model 'AdminSetting'
        db.create_table('newman_adminsetting', (
            ('var', models.SlugField(_('Variable'), max_length=64)),
            ('group', CachedForeignKey(orm['auth.Group'], null=True, verbose_name=_('Group'), blank=True)),
            ('id', models.AutoField(primary_key=True)),
            ('val', models.TextField(_('Value'))),
            ('user', CachedForeignKey(orm['auth.User'], null=True, verbose_name=_('User'), blank=True)),
        ))
        db.send_create_signal('newman', ['AdminSetting'])
        
        # Adding model 'AdminUserDraft'
        db.create_table('newman_adminuserdraft', (
            ('title', models.CharField(_('Title'), max_length=64, blank=True)),
            ('ts', models.DateTimeField(auto_now=True, editable=False)),
            ('user', CachedForeignKey(orm['auth.User'], verbose_name=_('User'))),
            ('data', models.TextField(_('Data'))),
            ('id', models.AutoField(primary_key=True)),
            ('ct', CachedForeignKey(orm['contenttypes.ContentType'], verbose_name=_('Model'))),
        ))
        db.send_create_signal('newman', ['AdminUserDraft'])
        
        # Adding model 'DenormalizedCategoryUserRole'
        db.create_table('newman_denormalizedcategoryuserrole', (
            ('user_id', models.IntegerField()),
            ('permission_codename', models.CharField(max_length=100)),
            ('permission_id', models.IntegerField()),
            ('root_category_id', models.IntegerField()),
            ('contenttype_id', models.IntegerField()),
            ('category_id', models.IntegerField()),
            ('id', models.AutoField(primary_key=True)),
        ))
        db.send_create_signal('newman', ['DenormalizedCategoryUserRole'])
        
        # Adding model 'AdminHelpItem'
        db.create_table('newman_adminhelpitem', (
            ('lang', models.CharField(_('Language'), max_length=5)),
            ('short', models.CharField(_('Short help'), max_length=255)),
            ('long', models.TextField(_('Full message'), blank=True)),
            ('field', models.CharField(_('Field'), max_length=64, blank=True)),
            ('id', models.AutoField(primary_key=True)),
            ('ct', CachedForeignKey(orm['contenttypes.ContentType'], verbose_name=_('Model'))),
        ))
        db.send_create_signal('newman', ['AdminHelpItem'])
        
        # Adding model 'CategoryUserRole'
        db.create_table('newman_categoryuserrole', (
            ('group', models.ForeignKey(orm['auth.Group'])),
            ('id', models.AutoField(primary_key=True)),
            ('user', models.ForeignKey(orm['auth.User'])),
        ))
        db.send_create_signal('newman', ['CategoryUserRole'])
        
        # Adding ManyToManyField 'CategoryUserRole.category'
        db.create_table('newman_categoryuserrole_category', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('categoryuserrole', models.ForeignKey(CategoryUserRole, null=False)),
            ('category', models.ForeignKey(Category, null=False))
        ))
        
    
    
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
        
    
    
    models = {
        'core.category': {
            'Meta': {'ordering': "('site','tree_path',)", 'unique_together': "(('site','tree_path'),)", 'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
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
        'auth.group': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'newman.categoryuserrole': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    
