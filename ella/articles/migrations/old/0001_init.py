from django.utils.translation import ugettext_lazy as _

from south.db import db
from django.db import models
from ella.articles.models import *

class Migration:

    depends_on = (
        ("core", "0001_initial"),
    )
    
    def forwards(self, orm):
        
        # Adding model 'ArticleContents'
        db.create_table('articles_articlecontents', (
            ('content', models.TextField(_('Content'))),
            ('article', models.ForeignKey(orm.Article, verbose_name=_('Article'))),
            ('id', models.AutoField(primary_key=True)),
            ('title', models.CharField(_('Title'), max_length=200, blank=True)),
        ))
        db.send_create_signal('articles', ['ArticleContents'])
        
        # Adding model 'InfoBox'
        db.create_table('articles_infobox', (
            ('content', models.TextField(_('Content'))),
            ('updated', models.DateTimeField(_('Updated'), null=True, blank=True)),
            ('created', models.DateTimeField(_('Created'), default=datetime.now, editable=False)),
            ('id', models.AutoField(primary_key=True)),
            ('title', models.CharField(_('Title'), max_length=255)),
        ))
        db.send_create_signal('articles', ['InfoBox'])
        
        # Adding model 'Article'
        db.create_table('articles_article', (
            ('category', models.ForeignKey(orm['core.Category'], verbose_name=_('Category'))),
            ('updated', models.DateTimeField(_('Updated'), null=True, blank=True)),
            ('description', models.TextField(_('Description'))),
            ('title', models.CharField(_('Title'), max_length=255)),
            ('photo', models.ForeignKey(orm['photos.Photo'], null=True, verbose_name=_('Photo'), blank=True)),
            ('created', models.DateTimeField(_('Created'), default=datetime.now, editable=False, db_index=True)),
            ('upper_title', models.CharField(_('Upper title'), max_length=255, blank=True)),
            ('id', models.AutoField(primary_key=True)),
            ('source', models.ForeignKey(orm['core.Source'], null=True, verbose_name=_('Source'), blank=True)),
            ('content_type', models.ForeignKey(orm['contenttypes.ContentType'])),
            ('publishable_ptr', models.OneToOneField(orm['core.Publishable'])),
            ('slug', models.SlugField(_('Slug'), max_length=255)),
        ))
        db.send_create_signal('articles', ['Article'])
        
        # Adding ManyToManyField 'Article.authors'
        db.create_table('core_publishable_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('publishable', models.ForeignKey(Article, null=False)),
            ('author', models.ForeignKey(orm['core.Author'], null=False))
        ))
        
    
    
    def backwards(self):
        
        # Deleting model 'ArticleContents'
        db.delete_table('articles_articlecontents')
        
        # Deleting model 'InfoBox'
        db.delete_table('articles_infobox')
        
        # Deleting model 'Article'
        db.delete_table('articles_article')
        
        # Dropping ManyToManyField 'Article.authors'
        db.delete_table('core_publishable_authors')
        
    
    
    models = {
        'core.category': {
            'Meta': {'ordering': "('site','tree_path',)", 'unique_together': "(('site','tree_path'),)", 'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'photos.photo': {
            'Meta': {'ordering': "('-created',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.publishable': {
            'Meta': {'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'articles.article': {
            'Meta': {'ordering': "('-created',)"},
            '_stub': True,
            'publishable_ptr': ('models.OneToOneField', ['Publishable'], {})
        },
        'core.source': {
            'Meta': {'ordering': "('name',)", 'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.author': {
            'Meta': {'ordering': "('name','slug',)", 'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    
