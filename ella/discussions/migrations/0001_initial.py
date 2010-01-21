
from south.db import db
from django.db import models
from ella.discussions.models import *
import datetime

class Migration:
    
    depends_on = (
        ("core", "0001_initial"),
        ("photos", "0001_initial"),
        ("oldcomments", "0001_initial"),
    )
 
    def forwards(self, orm):
        
        # Adding model 'BannedUser'
        db.create_table('discussions_banneduser', (
            ('id', models.AutoField(primary_key=True)),
            ('user', models.ForeignKey(orm['auth.User'], related_name='banned_user')),
        ))
        db.send_create_signal('discussions', ['BannedUser'])
        
        # Adding model 'TopicThread'
        db.create_table('discussions_topicthread', (
            ('id', models.AutoField(primary_key=True)),
            ('title', models.CharField(_('Title'), max_length=255)),
            ('slug', models.SlugField(_('Slug'), max_length=255)),
            ('created', models.DateTimeField(_('Created'), default=datetime.datetime.now, editable=False)),
            ('author', models.ForeignKey(orm['auth.User'], null=True, verbose_name=_('authorized author'), blank=True)),
            ('nickname', models.CharField(_("Anonymous author's nickname"), max_length=50, blank=True)),
            ('email', models.EmailField(_('Authors email (optional)'), blank=True)),
            ('topic', models.ForeignKey(orm.Topic)),
            ('hit_counts', models.PositiveIntegerField(default=0)),
        ))
        db.send_create_signal('discussions', ['TopicThread'])
        
        # Adding model 'BannedString'
        db.create_table('discussions_bannedstring', (
            ('id', models.AutoField(primary_key=True)),
            ('expression', models.CharField(_('Expression'), max_length=20, db_index=True)),
            ('isregexp', models.BooleanField(default=False)),
        ))
        db.send_create_signal('discussions', ['BannedString'])
        
        # Adding model 'Topic'
        db.create_table('discussions_topic', (
            ('id', models.AutoField(primary_key=True)),
            ('title', models.CharField(_('Title'), max_length=255)),
            ('description', models.TextField(_('Description'))),
            ('slug', models.SlugField(_('Slug'), max_length=255)),
            ('category', models.ForeignKey(orm['core.Category'], verbose_name=_('Category'))),
            ('photo', models.ForeignKey(orm['photos.Photo'], null=True, verbose_name=_('Photo'), blank=True)),
            ('created', models.DateTimeField(_('Created'), default=datetime.datetime.now, editable=False)),
        ))
        db.send_create_signal('discussions', ['Topic'])
        
        # Adding model 'PostViewed'
        db.create_table('discussions_postviewed', (
            ('id', models.AutoField(primary_key=True)),
            ('target_ct', models.ForeignKey(orm['contenttypes.ContentType'], verbose_name=_('Target content type'))),
            ('target_id', models.PositiveIntegerField(_('Target id'))),
            ('user', models.ForeignKey(orm['auth.User'])),
        ))
        db.send_create_signal('discussions', ['PostViewed'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'BannedUser'
        db.delete_table('discussions_banneduser')
        
        # Deleting model 'TopicThread'
        db.delete_table('discussions_topicthread')
        
        # Deleting model 'BannedString'
        db.delete_table('discussions_bannedstring')
        
        # Deleting model 'Topic'
        db.delete_table('discussions_topic')
        
        # Deleting model 'PostViewed'
        db.delete_table('discussions_postviewed')
        
    
    
    models = {
        'core.category': {
            'Meta': {'ordering': "('site','tree_path',)", 'unique_together': "(('site','tree_path'),)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'discussions.topicthread': {
            'author': ('models.ForeignKey', ["orm['auth.User']"], {'null': 'True', 'verbose_name': "_('authorized author')", 'blank': 'True'}),
            'created': ('models.DateTimeField', ["_('Created')"], {'default': 'datetime.datetime.now', 'editable': 'False'}),
            'email': ('models.EmailField', ["_('Authors email (optional)')"], {'blank': 'True'}),
            'hit_counts': ('models.PositiveIntegerField', [], {'default': '0'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'nickname': ('models.CharField', ['_("Anonymous author\'s nickname")'], {'max_length': '50', 'blank': 'True'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '255'}),
            'topic': ('models.ForeignKey', ["orm['discussions.Topic']"], {})
        },
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'photos.photo': {
            'Meta': {'ordering': "('-created',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'discussions.bannedstring': {
            'expression': ('models.CharField', ["_('Expression')"], {'max_length': '20', 'db_index': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'isregexp': ('models.BooleanField', [], {'default': 'False'})
        },
        'discussions.postviewed': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'target_ct': ('models.ForeignKey', ["orm['contenttypes.ContentType']"], {'verbose_name': "_('Target content type')"}),
            'target_id': ('models.PositiveIntegerField', ["_('Target id')"], {}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {})
        },
        'discussions.banneduser': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'related_name': "'banned_user'"})
        },
        'discussions.topic': {
            'Meta': {'ordering': "('-created',)"},
            'category': ('models.ForeignKey', ["orm['core.Category']"], {'verbose_name': "_('Category')"}),
            'created': ('models.DateTimeField', ["_('Created')"], {'default': 'datetime.datetime.now', 'editable': 'False'}),
            'description': ('models.TextField', ["_('Description')"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'photo': ('models.ForeignKey', ["orm['photos.Photo']"], {'null': 'True', 'verbose_name': "_('Photo')", 'blank': 'True'}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '255'})
        }
    }
    
    complete_apps = ['discussions']
