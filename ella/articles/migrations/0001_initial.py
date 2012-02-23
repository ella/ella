
from south.db import db
from django.db import models
import datetime
from south.v2 import SchemaMigration
from ella.core.models import Publishable

class Migration(SchemaMigration):

    depends_on = (
        ("core", "0002_initial_publishable"),
    )

    def forwards(self, orm):
        # Adding model 'Article'
        db.create_table('articles_article', (
            ('publishable_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=Publishable, unique=True, primary_key=True)),
            ('upper_title', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, db_index=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('articles', ['Article'])

        # Adding model 'ArticleContents'
        db.create_table('articles_articlecontents', (
            ('id', models.AutoField(primary_key=True)),
            ('article', models.ForeignKey(orm['articles.Article'], verbose_name=_('Article'))),
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
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.category': {
            'Meta': {'ordering': "('site','tree_path',)", 'unique_together': "(('site','tree_path'),)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.publishable': {
            'Meta': {'object_name': 'Publishable'},
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Author']", 'symmetrical': 'False'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Category']"}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'photo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['photos.Photo']", 'null': 'True', 'blank': 'True'}),
            'publish_from': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(3000, 1, 1, 0, 0, 0, 2)', 'db_index': 'True'}),
            'publish_to': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Source']", 'null': 'True', 'blank': 'True'}),
            'static': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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
            'Meta': {'object_name': 'Article', '_ormbases': ['core.Publishable']},
            'content': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            'publishable_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Publishable']", 'unique': 'True', 'primary_key': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'upper_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
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
