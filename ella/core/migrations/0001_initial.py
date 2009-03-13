from django.utils.translation import ugettext_lazy as _

from south.db import db
from django.db import models
from ella.core.models import *

class Migration:
    
    def forwards(self):
        
        
        # Mock Models
        User = db.mock_model(model_name='User', db_table='auth_user', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        
        # Model 'Author'
        db.create_table('core_author', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(User, blank=True, null=True)),
            ('name', models.CharField(_('Name'), max_length=200, blank=True)),
            ('slug', models.SlugField(_('Slug'), max_length=255, unique=True)),
            ('description', models.TextField(_('Description'), blank=True)),
            ('text', models.TextField(_('Text'), blank=True)),
        ))
        # Model 'Source'
        db.create_table('core_source', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField(_('Name'), max_length=200)),
            ('url', models.URLField(_('URL'), blank=True)),
            ('description', models.TextField(_('Description'), blank=True)),
        ))
        
        # Mock Models
        Category = db.mock_model(model_name='Category', db_table='core_category', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        Site = db.mock_model(model_name='Site', db_table='django_site', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        
        # Model 'Category'
        db.create_table('core_category', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('title', models.CharField(_("Category Title"), max_length=200)),
            ('slug', models.SlugField(_('Slug'), max_length=255)),
            ('tree_parent', models.ForeignKey(Category, null=True, blank=True, verbose_name=_("Parent Category"))),
            ('tree_path', models.CharField(verbose_name=_("Path from root category"), max_length=255, editable=False)),
            ('description', models.TextField(_("Category Description"), blank=True)),
            ('site', models.ForeignKey(Site)),
        ))
        db.create_index('core_category', ['site_id','tree_path'], unique=True, db_tablespace='')
        
        
        # Mock Models
        ContentType = db.mock_model(model_name='ContentType', db_table='django_content_type', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        ContentType = db.mock_model(model_name='ContentType', db_table='django_content_type', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        
        # Model 'Related'
        db.create_table('core_related', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('target_ct', models.ForeignKey(ContentType, related_name='relation_for_set')),
            ('target_id', models.IntegerField()),
            ('source_ct', models.ForeignKey(ContentType, related_name='related_on_set')),
            ('source_id', models.IntegerField()),
        ))
        
        # Mock Models
        ContentType = db.mock_model(model_name='ContentType', db_table='django_content_type', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        Category = db.mock_model(model_name='Category', db_table='core_category', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        Source = db.mock_model(model_name='Source', db_table='core_source', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        Photo = db.mock_model(model_name='Photo', db_table='photos_photo', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        
        # Model 'Publishable'
        db.create_table('core_publishable', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('content_type', models.ForeignKey(ContentType)),
            ('category', models.ForeignKey(Category, verbose_name=_(Category))),
            ('title', models.CharField(_('Title'), max_length=255)),
            ('slug', models.SlugField(_('Slug'), max_length=255)),
            ('source', models.ForeignKey(Source, blank=True, null=True, verbose_name=_(Source))),
            ('photo', models.ForeignKey(Photo, blank=True, null=True, verbose_name=_(Photo))),
            ('description', models.TextField(_('Description'))),
        ))
        # Mock Models
        Publishable = db.mock_model(model_name='Publishable', db_table='core_publishable', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        Author = db.mock_model(model_name='Author', db_table='core_author', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        
        # M2M field 'Publishable.authors'
        db.create_table('core_publishable_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('publishable', models.ForeignKey(Publishable, null=False)),
            ('author', models.ForeignKey(Author, null=False))
        )) 
        
        # Mock Models
        Publishable = db.mock_model(model_name='Publishable', db_table='core_publishable', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        Category = db.mock_model(model_name='Category', db_table='core_category', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        
        # Model 'Placement'
        db.create_table('core_placement', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('publishable', models.ForeignKey(Publishable)),
            ('category', models.ForeignKey(Category, db_index=True)),
            ('publish_from', models.DateTimeField(_("Start of visibility"))),
            ('publish_to', models.DateTimeField(_("End of visibility"), null=True, blank=True)),
            ('slug', models.SlugField(_('Slug'), max_length=255, blank=True)),
            ('static', models.BooleanField(default=False)),
        ))
        
        # Mock Models
        Placement = db.mock_model(model_name='Placement', db_table='core_placement', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        Category = db.mock_model(model_name='Category', db_table='core_category', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        
        # Model 'Listing'
        db.create_table('core_listing', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('placement', models.ForeignKey(Placement)),
            ('category', models.ForeignKey(Category, db_index=True)),
            ('publish_from', models.DateTimeField(_("Start of listing"))),
            ('priority_from', models.DateTimeField(_("Start of prioritized listing"), null=True, blank=True)),
            ('priority_to', models.DateTimeField(_("End of prioritized listing"), null=True, blank=True)),
            ('priority_value', models.IntegerField(_("Priority"), blank=True, null=True)),
            ('remove', models.BooleanField(_("Remove"), help_text=_("Remove object from listing after the priority wears off?"), default=False)),
            ('commercial', models.BooleanField(_("Commercial"), default=False, help_text=_("Check this if the listing is of a commercial content."))),
        ))
        
        # Mock Models
        Placement = db.mock_model(model_name='Placement', db_table='core_placement', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        
        # Model 'HitCount'
        db.create_table('core_hitcount', (
            ('placement', models.ForeignKey(Placement, primary_key=True)),
            ('last_seen', models.DateTimeField(_('Last seen'), editable=False)),
            ('hits', models.PositiveIntegerField(_('Hits'), default=1)),
        ))
        
        db.send_create_signal('core', ['Author','Source','Category','Related','Publishable','Placement','Listing','HitCount'])
    
    def backwards(self):
        db.delete_table('core_hitcount')
        db.delete_table('core_listing')
        db.delete_table('core_placement')
        db.delete_table('core_publishable_authors')
        db.delete_table('core_publishable')
        db.delete_table('core_related')
        db.delete_table('core_category')
        db.delete_table('core_source')
        db.delete_table('core_author')
        
