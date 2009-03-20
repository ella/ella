
from south.db import db
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ella.core.models import *
from ella.legacy.models import *

class Migration:

    def forwards(self, orm):
        "Write your forwards migration here"

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

        # TODO:
        # migrate as much as possible to south db api
        db.execute_many('''
# move the data
# articles
INSERT INTO
    `core_publishable` (old_id, title, slug, category_id, source_id, photo_id, description, content_type_id)
    SELECT
        a.id, title, slug, category_id, source_id, photo_id, perex, ct.id
    FROM
        `articles_article` a, `django_content_type` ct
    WHERE
        ct.`app_label` = 'articles' AND  ct.`model` = 'article';

# events
INSERT INTO
    `core_publishable` (old_id, title, slug, category_id, source_id, photo_id, description, content_type_id)
    SELECT
        a.id, title, slug, category_id, source_id, photo_id, perex, ct.id
    FROM
        `events_event` a, `django_content_type` ct
    WHERE
        ct.`app_label` = 'events' AND  ct.`model` = 'event';

        ''')

        # add link to parent
        db.add_column('articles_article', 'publishable_ptr_id', models.IntegerField(null=True))
        db.add_column('events_event', 'publishable_ptr_id', models.IntegerField(null=True))

        db.execute_many('''
# update the link
UPDATE
    `core_publishable` pub INNER JOIN `articles_article` art ON (art.`id` = pub.`old_id`)
    SET
        art.`publishable_ptr_id` = pub.`id`
  WHERE
    pub.`content_type_id` = (SELECT ct.`id` FROM `django_content_type` ct WHERE ct.`app_label` = 'articles' AND  ct.`model` = 'article');

UPDATE
    `core_publishable` pub INNER JOIN `events_event` art ON (art.`id` = pub.`old_id`)
    SET
        art.`publishable_ptr_id` = pub.`id`
  WHERE
    pub.`content_type_id` = (SELECT ct.`id` FROM `django_content_type` ct WHERE ct.`app_label` = 'events' AND  ct.`model` = 'event');

# drop PRIMARY KEY
ALTER TABLE `articles_article_authors` DROP FOREIGN KEY `article_id_refs_id_1bb2108a`;
ALTER TABLE `articles_article` CHANGE `id` `id` integer NULL;
ALTER TABLE `articles_article` DROP PRIMARY KEY;

ALTER TABLE `events_event_authors` DROP FOREIGN KEY `event_id_refs_id_2b6d1de2`;
ALTER TABLE `events_event` CHANGE `id` `id` integer NULL;
ALTER TABLE `events_event` DROP PRIMARY KEY;

# replace it with a link to parent
ALTER TABLE  `articles_article` CHANGE COLUMN `publishable_ptr_id` `publishable_ptr_id` integer NOT NULL PRIMARY KEY;
ALTER TABLE `articles_article` ADD CONSTRAINT `publishable_ptr_id_refs_id_39133a3e` FOREIGN KEY (`publishable_ptr_id`) REFERENCES `core_publishable` (`id`);

ALTER TABLE  `events_event` CHANGE COLUMN `publishable_ptr_id` `publishable_ptr_id` integer NOT NULL PRIMARY KEY;
ALTER TABLE `events_event` ADD CONSTRAINT `publishable_ptr_id_refs_id_fb35fe` FOREIGN KEY (`publishable_ptr_id`) REFERENCES `core_publishable` (`id`);

# UPDATE m2m relations
INSERT INTO `core_publishable_authors` (`publishable_id`, `author_id`)
  SELECT
    art.`publishable_ptr_id`, art_aut.`author_id`
  FROM
    `articles_article` art INNER JOIN `articles_article_authors` art_aut ON (art.`id` = art_aut.`article_id`);
DROP TABLE `articles_article_authors`;

INSERT INTO `core_publishable_authors` (`publishable_id`, `author_id`)
  SELECT
    art.`publishable_ptr_id`, art_aut.`author_id`
  FROM
    `events_event` art INNER JOIN `events_event_authors` art_aut ON (art.`id` = art_aut.`event_id`);
DROP TABLE `events_event_authors`;

# UPDATE generic relations
# articles
UPDATE
    `tagging_taggeditem` gen INNER JOIN `core_publishable` pub ON (gen.`content_type_id` = pub.`content_type_id` AND gen.`object_id` = pub.`old_id`)
  SET
    gen.`object_id` = pub.`id`
  WHERE
    pub.`content_type_id` = (SELECT ct.`id` FROM `django_content_type` ct WHERE ct.`app_label` = 'articles' AND  ct.`model` = 'article');

UPDATE
    `comments_comment` gen INNER JOIN `core_publishable` pub ON (gen.`target_ct_id` = pub.`content_type_id` AND gen.`target_id` = pub.`old_id`)
  SET
    gen.`target_id` = pub.`id`
  WHERE
    pub.`content_type_id` = (SELECT ct.`id` FROM `django_content_type` ct WHERE ct.`app_label` = 'articles' AND  ct.`model` = 'article');
# events
UPDATE
    `tagging_taggeditem` gen INNER JOIN `core_publishable` pub ON (gen.`content_type_id` = pub.`content_type_id` AND gen.`object_id` = pub.`old_id`)
  SET
    gen.`object_id` = pub.`id`
  WHERE
    pub.`content_type_id` = (SELECT ct.`id` FROM `django_content_type` ct WHERE ct.`app_label` = 'events' AND  ct.`model` = 'event');

UPDATE
    `comments_comment` gen INNER JOIN `core_publishable` pub ON (gen.`target_ct_id` = pub.`content_type_id` AND gen.`target_id` = pub.`old_id`)
  SET
    gen.`target_id` = pub.`id`
  WHERE
    pub.`content_type_id` = (SELECT ct.`id` FROM `django_content_type` ct WHERE ct.`app_label` = 'events' AND  ct.`model` = 'event');

ALTER TABLE `articles_article` DROP FOREIGN KEY `photo_id_refs_id_573d4575`;
        ''')

        # drop duplicate columns
        for table in ['articles_article', 'events_event']:
            for column in ['title', 'category_id', 'photo_id', 'source_id', 'slug', 'id', 'perex']:
                db.delete_column(table, column)

        db.add_column('core_placement', 'publishable_id', models.IntegerField(null=True))

        db.execute_many('''

# MIGRATE PLACEMENTS
UPDATE
  `core_placement` plac INNER JOIN `core_publishable` pub ON (plac.`target_ct_id` = pub.`content_type_id` AND plac.`target_id` = pub.`old_id`)
SET
  plac.`publishable_id` = pub.`id`
WHERE
  pub.`content_type_id` = (SELECT ct.`id` FROM `django_content_type` ct WHERE ct.`app_label` = 'events' AND  ct.`model` = 'event');

UPDATE
  `core_placement` plac INNER JOIN `core_publishable` pub ON (plac.`target_ct_id` = pub.`content_type_id` AND plac.`target_id` = pub.`old_id`)
SET
  plac.`publishable_id` = pub.`id`
WHERE
  pub.`content_type_id` = (SELECT ct.`id` FROM `django_content_type` ct WHERE ct.`app_label` = 'articles' AND  ct.`model` = 'article');

ALTER TABLE  `core_placement` CHANGE COLUMN `publishable_id` `publishable_id` integer NOT NULL;
ALTER TABLE `core_placement` ADD CONSTRAINT `publishable_id_refs_id_37a3a539` FOREIGN KEY (`publishable_id`) REFERENCES `core_publishable` (`id`);
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


