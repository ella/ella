
from south.db import db
from django.db import models
from ella.core.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Category'
        db.create_table('core_category', (
            ('id', models.AutoField(primary_key=True)),
            ('title', models.CharField(_("Category Title"), max_length=200)),
            ('slug', models.SlugField(_('Slug'), max_length=255)),
            ('tree_parent', models.ForeignKey(orm.Category, null=True, verbose_name=_("Parent Category"), blank=True)),
            ('tree_path', models.CharField(editable=False, max_length=255, verbose_name=_("Path from root category"))),
            ('description', models.TextField(_("Category Description"), blank=True)),
            ('site', models.ForeignKey(orm['sites.Site'])),
        ))
        db.send_create_signal('core', ['Category'])
        
        # Adding model 'Placement'
        db.create_table('core_placement', (
            ('id', models.AutoField(primary_key=True)),
            ('target_ct', models.ForeignKey(orm['contenttypes.ContentType'])),
            ('target_id', models.IntegerField()),
            ('category', models.ForeignKey(orm.Category, db_index=True)),
            ('publish_from', models.DateTimeField(_("Start of visibility"))),
            ('publish_to', models.DateTimeField(_("End of visibility"), null=True, blank=True)),
            ('slug', models.SlugField(_('Slug'), max_length=255, blank=True)),
            ('static', models.BooleanField(default=False)),
        ))
        db.send_create_signal('core', ['Placement'])
        
        # Adding model 'Listing'
        db.create_table('core_listing', (
            ('id', models.AutoField(primary_key=True)),
            ('placement', models.ForeignKey(orm.Placement)),
            ('category', models.ForeignKey(orm.Category, db_index=True)),
            ('publish_from', models.DateTimeField(_("Start of listing"))),
            ('priority_from', models.DateTimeField(_("Start of prioritized listing"), null=True, blank=True)),
            ('priority_to', models.DateTimeField(_("End of prioritized listing"), null=True, blank=True)),
            ('priority_value', models.IntegerField(_("Priority"), null=True, blank=True)),
            ('remove', models.BooleanField(_("Remove"), default=False)),
            ('commercial', models.BooleanField(_("Commercial"), default=False)),
        ))
        db.send_create_signal('core', ['Listing'])
        
        # Adding model 'HitCount'
        db.create_table('core_hitcount', (
            ('placement', models.ForeignKey(orm.Placement, primary_key=True)),
            ('last_seen', models.DateTimeField(_('Last seen'), editable=False)),
            ('hits', models.PositiveIntegerField(_('Hits'), default=1)),
        ))
        db.send_create_signal('core', ['HitCount'])
        
        # Adding model 'Related'
        db.create_table('core_related', (
            ('id', models.AutoField(primary_key=True)),
            ('target_ct', models.ForeignKey(orm['contenttypes.ContentType'], related_name='relation_for_set')),
            ('target_id', models.IntegerField()),
            ('source_ct', models.ForeignKey(orm['contenttypes.ContentType'], related_name='related_on_set')),
            ('source_id', models.IntegerField()),
        ))
        db.send_create_signal('core', ['Related'])
        
        # Adding model 'Source'
        db.create_table('core_source', (
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(_('Name'), max_length=200)),
            ('url', models.URLField(_('URL'), blank=True)),
            ('description', models.TextField(_('Description'), blank=True)),
        ))
        db.send_create_signal('core', ['Source'])
        
        # Adding model 'Author'
        db.create_table('core_author', (
            ('id', models.AutoField(primary_key=True)),
            ('user', models.ForeignKey(orm['auth.User'], null=True, blank=True)),
            ('name', models.CharField(_('Name'), max_length=200, blank=True)),
            ('slug', models.SlugField(_('Slug'), unique=True, max_length=255)),
            ('description', models.TextField(_('Description'), blank=True)),
            ('text', models.TextField(_('Text'), blank=True)),
        ))
        db.send_create_signal('core', ['Author'])
        
        # Creating unique_together for [site, tree_path] on Category.
        db.create_unique('core_category', ['site_id', 'tree_path'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Category'
        db.delete_table('core_category')
        
        # Deleting model 'Placement'
        db.delete_table('core_placement')
        
        # Deleting model 'Listing'
        db.delete_table('core_listing')
        
        # Deleting model 'HitCount'
        db.delete_table('core_hitcount')
        
        # Deleting model 'Related'
        db.delete_table('core_related')
        
        # Deleting model 'Source'
        db.delete_table('core_source')
        
        # Deleting model 'Author'
        db.delete_table('core_author')
        
        # Deleting unique_together for [site, tree_path] on Category.
        db.delete_unique('core_category', ['site_id', 'tree_path'])
        
    
    
    models = {
        'core.category': {
            'Meta': {'ordering': "('site','tree_path',)", 'unique_together': "(('site','tree_path'),)"},
            'description': ('models.TextField', ['_("Category Description")'], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'site': ('models.ForeignKey', ["orm['sites.Site']"], {}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'title': ('models.CharField', ['_("Category Title")'], {'max_length': '200'}),
            'tree_parent': ('models.ForeignKey', ["orm['core.Category']"], {'null': 'True', 'verbose_name': '_("Parent Category")', 'blank': 'True'}),
            'tree_path': ('models.CharField', [], {'editable': 'False', 'max_length': '255', 'verbose_name': '_("Path from root category")'})
        },
        'core.placement': {
            'Meta': {'ordering': "('-publish_from',)"},
            'category': ('models.ForeignKey', ["orm['core.Category']"], {'db_index': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'publish_from': ('models.DateTimeField', ['_("Start of visibility")'], {}),
            'publish_to': ('models.DateTimeField', ['_("End of visibility")'], {'null': 'True', 'blank': 'True'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255', 'blank': 'True'}),
            'static': ('models.BooleanField', [], {'default': 'False'}),
            'target_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {}),
            'target_id': ('models.IntegerField', [], {})
        },
        'core.listing': {
            'Meta': {'ordering': "('-publish_from',)"},
            'category': ('models.ForeignKey', ["orm['core.Category']"], {'db_index': 'True'}),
            'commercial': ('models.BooleanField', ['_("Commercial")'], {'default': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'placement': ('models.ForeignKey', ["orm['core.Placement']"], {}),
            'priority_from': ('models.DateTimeField', ['_("Start of prioritized listing")'], {'null': 'True', 'blank': 'True'}),
            'priority_to': ('models.DateTimeField', ['_("End of prioritized listing")'], {'null': 'True', 'blank': 'True'}),
            'priority_value': ('models.IntegerField', ['_("Priority")'], {'null': 'True', 'blank': 'True'}),
            'publish_from': ('models.DateTimeField', ['_("Start of listing")'], {}),
            'remove': ('models.BooleanField', ['_("Remove")'], {'default': 'False'})
        },
        'core.hitcount': {
            'hits': ('models.PositiveIntegerField', ["_('Hits')"], {'default': '1'}),
            'last_seen': ('models.DateTimeField', ["_('Last seen')"], {'editable': 'False'}),
            'placement': ('models.ForeignKey', ["orm['core.Placement']"], {'primary_key': 'True'})
        },
        'core.related': {
            'Meta': {'ordering': "('source_ct','source_id',)"},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'source_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'related_name': "'related_on_set'"}),
            'source_id': ('models.IntegerField', [], {}),
            'target_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'related_name': "'relation_for_set'"}),
            'target_id': ('models.IntegerField', [], {})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'db_table': "'django_site'"},
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
        'core.source': {
            'Meta': {'ordering': "('name',)"},
            'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ["_('Name')"], {'max_length': '200'}),
            'url': ('models.URLField', ["_('URL')"], {'blank': 'True'})
        },
        'core.author': {
            'Meta': {'ordering': "('name','slug',)"},
            'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ["_('Name')"], {'max_length': '200', 'blank': 'True'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'unique': 'True', 'max_length': '255'}),
            'text': ('models.TextField', ["_('Text')"], {'blank': 'True'}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'null': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['core']
