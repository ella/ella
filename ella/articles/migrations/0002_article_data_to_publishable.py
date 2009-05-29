
from south.db import db
from django.db import models
from ella.articles.models import *

from ella.core.migrations_base import BasePublishableDataMigration, alter_foreignkey_to_int

class Migration(BasePublishableDataMigration):

    app_label = 'articles'
    model = 'article'
    table = '%s_%s' % (app_label, model)

    publishable_uncommon_cols = {
        'source_id': 'source_id',
        'description': 'perex',
    }

    def alter_self_foreignkeys(self, orm):
        # migrate authors as in base
        super(Migration, self).alter_self_foreignkeys(orm)
        alter_foreignkey_to_int('articles_articlecontents', 'article')
        alter_foreignkey_to_int('recipes_oldrecipearticleredirect', 'new_id')

    def move_self_foreignkeys(self, orm):
        # migrate authors as in base
        super(Migration, self).move_self_foreignkeys(orm)

        # migrate new article IDs to articlecontents
        substitute = {}
        substitute.update(self.substitute)
        substitute.update({
            'table': 'articles_articlecontents',
            'fk_field': 'article_id',
        })
        db.execute('''
            UPDATE
                `%(table)s` tbl INNER JOIN `core_publishable` pub ON (tbl.`id` = pub.`old_id`)
            SET
                tbl.`%(fk_field)s` = pub.`id`
            WHERE
                pub.`content_type_id` = (SELECT ct.`id` FROM `django_content_type` ct WHERE ct.`app_label` = '%(app_label)s' AND ct.`model` = '%(model)s');
            ''' % substitute
        )
        db.alter_column(substitute['table'], substitute['fk_field'], models.ForeignKey(orm['%(app_label)s.%(model)s' % substitute]))

        # TODO: migrate new article IDs to oldrecipearticleredirect
        # ...

    freezed_models = {
        'articles.article': {
            'Meta': {'ordering': "('-created',)", '_bases': ['ella.core.models.publishable.Publishable']},
            'created': ('models.DateTimeField', ["_('Created')"], {'default': 'datetime.now', 'editable': 'False', 'db_index': 'True'}),
            'publishable_ptr': ('models.OneToOneField', ["orm['core.Publishable']"], {}),
            'updated': ('models.DateTimeField', ["_('Updated')"], {'null': 'True', 'blank': 'True'}),
            'upper_title': ('models.CharField', ["_('Upper title')"], {'max_length': '255', 'blank': 'True'})
        },
    }

