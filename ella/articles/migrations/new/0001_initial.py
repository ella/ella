
from south.db import db
from django.db import models
from ella.articles.models import *

class Migration:
    
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
            ('created', models.DateTimeField(_('Created'), default=datetime.now, editable=False)),
            ('updated', models.DateTimeField(_('Updated'), null=True, blank=True)),
            ('content', models.TextField(_('Content'))),
        ))
        db.send_create_signal('articles', ['InfoBox'])
        
        # Adding model 'Article'
        db.create_table('articles_article', (
            ('publishable_ptr', models.OneToOneField(orm['core.Publishable'])),
            ('upper_title', models.CharField(_('Upper title'), max_length=255, blank=True)),
            ('created', models.DateTimeField(_('Created'), default=datetime.now, editable=False, db_index=True)),
            ('updated', models.DateTimeField(_('Updated'), null=True, blank=True)),
        ))
        db.send_create_signal('articles', ['Article'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'ArticleContents'
        db.delete_table('articles_articlecontents')
        
        # Deleting model 'InfoBox'
        db.delete_table('articles_infobox')
        
        # Deleting model 'Article'
        db.delete_table('articles_article')
        
    
    
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
            'Meta': {'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.author': {
            'Meta': {'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        }
    }
    
    complete_apps = ['articles']
