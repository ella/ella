
from south.db import db
from django.db import models
from ella.articles.models import *
import datetime

class Migration:

    depends_on = (
        ("core", "0001_initial"),
        ("photos", "0001_initial"),
    )

    def forwards(self, orm):

        # Adding model 'ArticleContents'
        db.create_table('articles_articlecontents', (
            ('id', models.AutoField(primary_key=True)),
            ('article', models.ForeignKey(orm.Article, verbose_name=_('Article'))),
            ('title', models.CharField(_('Title'), max_length=200, blank=True)),
            ('content', models.TextField(_('Content'))),
        ))
        db.send_create_signal('articles', ['ArticleContents'])

        # Adding model 'InfoBox'
        db.create_table('articles_infobox', (
            ('id', models.AutoField(primary_key=True)),
            ('title', models.CharField(_('Title'), max_length=255)),
            ('created', models.DateTimeField(_('Created'), default=datetime.datetime.now, editable=False)),
            ('updated', models.DateTimeField(_('Updated'), null=True, blank=True)),
            ('content', models.TextField(_('Content'))),
        ))
        db.send_create_signal('articles', ['InfoBox'])

        # Adding model 'Article'
        db.create_table('articles_article', (
            ('id', models.AutoField(primary_key=True)),
            ('title', models.CharField(_('Title'), max_length=255)),
            ('upper_title', models.CharField(_('Upper title'), max_length=255, blank=True)),
            ('slug', models.SlugField(_('Slug'), max_length=255)),
            ('perex', models.TextField(_('Perex'))),
            ('created', models.DateTimeField(_('Created'), default=datetime.datetime.now, editable=False, db_index=True)),
            ('updated', models.DateTimeField(_('Updated'), null=True, blank=True)),
            ('source', models.ForeignKey(orm['core.Source'], null=True, verbose_name=_('Source'), blank=True)),
            ('category', models.ForeignKey(orm['core.Category'], verbose_name=_('Category'))),
            ('photo', models.ForeignKey(orm['photos.Photo'], null=True, verbose_name=_('Photo'), blank=True)),
        ))
        db.send_create_signal('articles', ['Article'])

        # Adding ManyToManyField 'Article.authors'
        db.create_table('articles_article_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('article', models.ForeignKey(orm.Article, null=False)),
            ('author', models.ForeignKey(orm['core.Author'], null=False))
        ))



    def backwards(self, orm):

        # Deleting model 'ArticleContents'
        db.delete_table('articles_articlecontents')

        # Deleting model 'InfoBox'
        db.delete_table('articles_infobox')

        # Deleting model 'Article'
        db.delete_table('articles_article')

        # Dropping ManyToManyField 'Article.authors'
        db.delete_table('articles_article_authors')



    models = {
        'core.category': {
            'Meta': {'ordering': "('site','tree_path',)", 'unique_together': "(('site','tree_path'),)"},
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
            'created': ('models.DateTimeField', ["_('Created')"], {'default': 'datetime.datetime.now', 'editable': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '255'}),
            'updated': ('models.DateTimeField', ["_('Updated')"], {'null': 'True', 'blank': 'True'})
        },
        'photos.photo': {
            'Meta': {'ordering': "('-created',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'articles.article': {
            'Meta': {'ordering': "('-created',)"},
            'authors': ('models.ManyToManyField', ["orm['core.Author']"], {'verbose_name': "_('Authors')"}),
            'category': ('models.ForeignKey', ["orm['core.Category']"], {'verbose_name': "_('Category')"}),
            'created': ('models.DateTimeField', ["_('Created')"], {'default': 'datetime.datetime.now', 'editable': 'False', 'db_index': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'perex': ('models.TextField', ["_('Perex')"], {}),
            'photo': ('models.ForeignKey', ["orm['photos.Photo']"], {'null': 'True', 'verbose_name': "_('Photo')", 'blank': 'True'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'source': ('models.ForeignKey', ["orm['core.Source']"], {'null': 'True', 'verbose_name': "_('Source')", 'blank': 'True'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '255'}),
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
