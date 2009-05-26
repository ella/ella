
from south.db import db
from django.db import models
from ella.articles.models import *

class Migration:

    def forwards(self, orm):

        # Adding field 'Article.publishable_ptr'
        db.add_column('articles_article', 'publishable_ptr', models.OneToOneField(orm['core.Publishable']))

        # Deleting field 'Article.category'
        db.delete_column('articles_article', 'category_id')

        # Deleting field 'Article.perex'
        db.delete_column('articles_article', 'perex')

        # Dropping ManyToManyField 'Article.authors'
        db.delete_table('articles_article_authors')

        # Deleting field 'Article.id'
        db.delete_column('articles_article', 'id')

        # Deleting field 'Article.slug'
        db.delete_column('articles_article', 'slug')

        # Deleting field 'Article.photo'
        db.delete_column('articles_article', 'photo_id')

        # Deleting field 'Article.source'
        db.delete_column('articles_article', 'source_id')

        # Deleting field 'Article.title'
        db.delete_column('articles_article', 'title')



    def backwards(self, orm):

        # Deleting field 'Article.publishable_ptr'
        db.delete_column('articles_article', 'publishable_ptr_id')

        # Adding field 'Article.category'
        db.add_column('articles_article', 'category', models.ForeignKey(orm['core.Category'], verbose_name=_('Category')))

        # Adding field 'Article.perex'
        db.add_column('articles_article', 'perex', models.TextField(_('Perex')))

        # Adding ManyToManyField 'Article.authors'
        db.create_table('articles_article_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('article', models.ForeignKey(orm.Article, null=False)),
            ('author', models.ForeignKey(orm['core.author'], null=False))
        ))

        # Adding field 'Article.id'
        db.add_column('articles_article', 'id', models.AutoField(primary_key=True))

        # Adding field 'Article.slug'
        db.add_column('articles_article', 'slug', models.SlugField(_('Slug'), max_length=255))

        # Adding field 'Article.photo'
        db.add_column('articles_article', 'photo', models.ForeignKey(orm['photos.Photo'], null=True, verbose_name=_('Photo'), blank=True))

        # Adding field 'Article.source'
        db.add_column('articles_article', 'source', models.ForeignKey(orm['core.Source'], null=True, verbose_name=_('Source'), blank=True))

        # Adding field 'Article.title'
        db.add_column('articles_article', 'title', models.CharField(_('Title'), max_length=255))



    models = {
        'core.category': {
            'Meta': {'unique_together': "(('site','tree_path'),)", 'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'articles.articlecontents': {
            'article': ('models.ForeignKey', ["orm['articles.Article']"], {'verbose_name': "_('Article')"}),
            'content': ('models.TextField', ["_('Content')"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '200', 'blank': 'True'})
        },
        'articles.infobox': {
            'Meta': {'ordering': "('-created',)"},
            'content': ('models.TextField', ["_('Content')"], {}),
            'created': ('models.DateTimeField', ["_('Created')"], {'default': 'datetime.now', 'editable': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '255'}),
            'updated': ('models.DateTimeField', ["_('Updated')"], {'null': 'True', 'blank': 'True'})
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
            'Meta': {'ordering': "('-created',)", '_bases': ['ella.core.models.publishable.Publishable']},
            'created': ('models.DateTimeField', ["_('Created')"], {'default': 'datetime.now', 'editable': 'False', 'db_index': 'True'}),
            'publishable_ptr': ('models.OneToOneField', ["orm['core.Publishable']"], {}),
            'updated': ('models.DateTimeField', ["_('Updated')"], {'null': 'True', 'blank': 'True'}),
            'upper_title': ('models.CharField', ["_('Upper title')"], {'max_length': '255', 'blank': 'True'})
        },
        'core.source': {
            'Meta': {'ordering': "('name',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.author': {
            'Meta': {'ordering': "('name','slug',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['articles']
