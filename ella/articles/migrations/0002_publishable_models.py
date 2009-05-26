
from south.db import db
from django.db import models
from ella.articles.models import *

class Migration:

    app_name = 'articles'
    module_name = 'article'

    depends_on = (
        ("core", "0002_publishable_models"),
    )

    def forwards(self, orm):
        # add a temporary column to remember the old ID
        db.add_column('core_publishable', 'old_id', models.IntegerField(null=True))

        # migrate publishables
        self.forwards_publishable(orm)
        # migrate generic relations
        #self.forwards_generic_relations(orm)
        # migrate placements
        #self.forwards_placements(orm)

        # delete temporary column to remember the old ID
        db.delete_column('core_publishable', 'old_id')

    def forwards_publishable(self, orm):
        '''
        creation of publishable objects

        TODO: sync publish_from
        '''
        app = self.app_name
        mod = self.module_name
        table = '%s_%s' (app, mod)

        # move the data
        db.execute('''
            INSERT INTO
                `core_publishable` (old_id, title, slug, category_id, source_id, photo_id, description, content_type_id)
            SELECT
                a.id, title, slug, category_id, source_id, photo_id, perex, ct.id
            FROM
                `%(table)s` a, `django_content_type` ct
            WHERE
                ct.`app_label` = '%(app)s' AND ct.`model` = '%(mod)s';
            ''' % {'app': app, 'mod': mod, 'table': table,}
        )

        # add link to parent
        db.add_column(table, 'publishable_ptr', models.IntegerField(null=True, blank=True))

        # update the link
        db.execute('''
            UPDATE
                `core_publishable` pub INNER JOIN `%(table)s` art ON (art.`id` = pub.`old_id`)
            SET
                art.`publishable_ptr_id` = pub.`id`
            WHERE
                pub.`content_type_id` = (SELECT ct.`id` FROM `django_content_type` ct WHERE ct.`app_label` = '%(app)s' AND ct.`model` = '%(mod)s');
            ''' % {'app': app, 'mod': mod, 'table': table,}
        )

        # drop foreign key constraint from intermediate table
        db.alter_column('%s_authors' % table, 'article', models.IntegerField())
        # drop primary key
        db.alter_column(table, 'id', models.IntegerField(null=True, blank=True))
        # replace it with a link to parent
        db.alter_column(table, 'publishable_ptr', models.OneToOneField(orm['core.Publishable']), null=False, blank=False)

        # update authors
        db.execute('''
            INSERT INTO
                `core_publishable_authors` (`publishable_id`, `author_id`)
            SELECT
                art.`publishable_ptr_id`, art_aut.`author_id`
            FROM
                `%(table)s` art INNER JOIN `%(table)s_authors` art_aut ON (art.`id` = art_aut.`%(mod)s`);
            ''' % {'app': app, 'mod': mod, 'table': table,}
        )
        db.delete_table('%s_authors' % table)

        # drop duplicate columns
        for column in ['title', 'category_id', 'photo_id', 'source_id', 'slug', 'id', 'perex']:
            db.delete_column(table, column)

    def forwards_generic_relations(self, orm):

        app = self.app_name
        mod = self.module_name
        table = '%s_%s' (app, mod)

        # UPDATE generic relations
        db.execute_many('''
                UPDATE
                    `tagging_taggeditem` gen INNER JOIN `core_publishable` pub ON (gen.`content_type_id` = pub.`content_type_id` AND gen.`object_id` = pub.`old_id`)
                SET
                    gen.`object_id` = pub.`id`
                WHERE
                    pub.`content_type_id` = (SELECT ct.`id` FROM `django_content_type` ct WHERE ct.`app_label` = '%(app)s' AND  ct.`model` = '%(mod)s');

                UPDATE
                    `comments_comment` gen INNER JOIN `core_publishable` pub ON (gen.`target_ct_id` = pub.`content_type_id` AND gen.`target_id` = pub.`old_id`)
                SET
                    gen.`target_id` = pub.`id`
                WHERE
                    pub.`content_type_id` = (SELECT ct.`id` FROM `django_content_type` ct WHERE ct.`app_label` = '%(app)s' AND  ct.`model` = '%(mod)s');
            ''' % {'app': app, 'mod': mod, 'table': table}
        )

    def forwards_placements(self, orm):

        app = self.app_name
        mod = self.module_name
        table = '%s_%s' (app, mod)

        db.add_column('core_placement', 'publishable_id', models.IntegerField(null=True))

        # MIGRATE PLACEMENTS
        db.execute('''
                UPDATE
                    `core_placement` plac INNER JOIN `core_publishable` pub ON (plac.`target_ct_id` = pub.`content_type_id` AND plac.`target_id` = pub.`old_id`)
                SET
                    plac.`publishable_id` = pub.`id`
                WHERE
                    pub.`content_type_id` = (SELECT ct.`id` FROM `django_content_type` ct WHERE ct.`app_label` = '%(app)s' AND  ct.`model` = '%(mod)s');
            ''' % {'app': app, 'mod': mod, 'table': table}
        )

        db.alter_column('core_placement', 'publishable_id', models.ForeignKey(Publishable))

        # TODO: move it via south
        db.execute('''
                ALTER TABLE `core_placement` DROP FOREIGN KEY `core_placement_ibfk_2`;
        ''')

        db.create_index('core_placement', ['publishable_id'])
        db.delete_column('core_placement', 'target_ct_id')
        db.delete_column('core_placement', 'target_id')

    def ___forwards_original(self, orm):

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
        "Write your backwards migration here"
        print 'there is no way back'

    def ___backwards_original(self, orm):

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
