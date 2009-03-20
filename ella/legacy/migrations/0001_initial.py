# TODO: work with ContentTypes' IDs instead of %(app)s and %(mod)s ??
from south.db import db
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ella.core.models import *
from ella.legacy.models import *


MODELS = [('articles', 'article'), ('events', 'event')]

class Migration:

    def forwards(self, orm):
        "Write your forwards migration here"
        # TODO:
        # migrate as much as possible to south db api

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
        # TODO: create ContentType for Publishable

        # Mock Models
        Publishable = db.mock_model(model_name='Publishable', db_table='core_publishable',
                db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})
        Author = db.mock_model(model_name='Author', db_table='core_author',
                db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField, pk_field_args=[], pk_field_kwargs={})

        # M2M field 'Publishable.authors'
        db.create_table('core_publishable_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('publishable', models.ForeignKey(Publishable, null=False)),
            ('author', models.ForeignKey(Author, null=False))
        ))


        # add a temporary column to remember the old ID
        db.add_column('core_publishable', 'old_id', models.IntegerField(null=True))

        for app, mod in MODELS:
            table = app + '_' + mod
            # move the data
            db.execute('''
                INSERT INTO
                    `core_publishable` (old_id, title, slug, category_id, source_id, photo_id, description, content_type_id)
                    SELECT
                        a.id, title, slug, category_id, source_id, photo_id, perex, ct.id
                    FROM
                        `%(table)s` a, `django_content_type` ct
                    WHERE
                        ct.`app_label` = '%(app)s' AND  ct.`model` = '%(mod)s';
                ''' % {'app':app, 'mod': mod, 'table': table}
            )

            # add link to parent
            db.add_column(table, 'publishable_ptr_id', models.IntegerField(null=True))

# update the link
            db.execute('''
                UPDATE
                    `core_publishable` pub INNER JOIN `%(table)s` art ON (art.`id` = pub.`old_id`)
                    SET
                        art.`publishable_ptr_id` = pub.`id`
                WHERE
                    pub.`content_type_id` = (SELECT ct.`id` FROM `django_content_type` ct WHERE ct.`app_label` = '%(app)s' AND  ct.`model` = '%(mod)s');
                ''' % {'app':app, 'mod': mod, 'table': table}
            )

        # TODO: we could use introspection to get the FK name in order to drop it, then we could also move this into the loop
        db.execute_many('''
# drop PRIMARY KEY
ALTER TABLE `articles_article_authors` DROP FOREIGN KEY `article_id_refs_id_1bb2108a`;
ALTER TABLE `articles_article` CHANGE `id` `id` integer NULL;
ALTER TABLE `articles_article` DROP PRIMARY KEY;

ALTER TABLE `events_event_authors` DROP FOREIGN KEY `event_id_refs_id_2b6d1de2`;
ALTER TABLE `events_event` CHANGE `id` `id` integer NULL;
ALTER TABLE `events_event` DROP PRIMARY KEY;
        ''')

        for app, mod in MODELS:
            table = app + '_' + mod

            # replace it with a link to parent
            db.alter_column(table, 'publishable_ptr_id', models.ForeignKey(orm['core.Publishable'], primary_key=True))
            # update authors
            db.execute(''' 
                    INSERT INTO `core_publishable_authors` (`publishable_id`, `author_id`)
                    SELECT
                        art.`publishable_ptr_id`, art_aut.`author_id`
                    FROM
                        `%(table)s` art INNER JOIN `%(tab)s_authors` art_aut ON (art.`id` = art_aut.`%(mod)s_id`);
                ''' % {'app':app, 'mod': mod, 'table': table}
            )
            db.delete_table(table + '_authors')

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
                ''' % {'app':app, 'mod': mod, 'table': table}
            )

        db.execute('''
            ALTER TABLE `articles_article` DROP FOREIGN KEY `photo_id_refs_id_573d4575`;
        ''')

        db.add_column('core_placement', 'publishable_id', models.IntegerField(null=True))

        for app, mod in MODELS:
            table = app + '_' + mod

            # drop duplicate columns
            for column in ['title', 'category_id', 'photo_id', 'source_id', 'slug', 'id', 'perex']:
                db.delete_column(table, column)


            # MIGRATE PLACEMENTS
            db.execute('''
                    UPDATE
                        `core_placement` plac INNER JOIN `core_publishable` pub ON (plac.`target_ct_id` = pub.`content_type_id` AND plac.`target_id` = pub.`old_id`)
                    SET
                        plac.`publishable_id` = pub.`id`
                    WHERE
                        pub.`content_type_id` = (SELECT ct.`id` FROM `django_content_type` ct WHERE ct.`app_label` = '%(app)s' AND  ct.`model` = '%(mod)s');
                ''' % {'app':app, 'mod': mod, 'table': table}
            )

        db.alter_column('core_placement', 'publishable_id', models.ForeignKey(orm['core.Publishable']))

        db.execute('''
            ALTER TABLE `core_placement` DROP FOREIGN KEY `core_placement_ibfk_2`;
        ''')

        db.create_index('core_placement', ['publishable_id'])
        db.delete_column('core_placement', 'target_ct_id')
        db.delete_column('core_placement', 'target_id')


        # delete temporary column to remember the old ID
        db.delete_column('core_publishable', 'old_id')


        # TODO: run migrate fake on all apps


    '''
    def backwards(self, orm):
        "Write your backwards migration here"
        print 'there is no way back'
    '''


    models = {

    }


