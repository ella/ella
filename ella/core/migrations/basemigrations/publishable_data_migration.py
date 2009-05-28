
from south.db import db
from django.db import models
from django.utils.datastructures import SortedDict

from ella.core.models import *


class BasePublishableDataMigration:

    depends_on = (
        ("core", "0001_initial"), # TODO publishable mig
    )

    app_label = ''
    model = ''
    table = '%s_%s' % (app_label, model)

    _publishable_default_cols = {
        'title': 'title',
        'slug': 'slug',
        'category_id': 'category_id', 
        'photo_id': 'photo_id', 
    }

    publishable_uncommon_cols = {}

    @property
    def publishable_cols(self):
        c = self._publishable_default_cols.copy()
        c.update(**self.publishable_uncommon_cols)
        return SortedDict(c)


    def forwards(self, orm):

        # add a temporary column on Core Publishable to remember the old ID
        db.add_column('core_publishable', 'old_id', models.IntegerField(null=True))

        # move the data
        db.execute('''
            INSERT INTO
                `core_publishable` (old_id, content_type_id, %(cols_to)s)
                SELECT
                    a.id, ct.id, %(cols_from)s
                FROM
                    `%(table)s` a, `django_content_type` ct
                WHERE
                    ct.`app_label` = '%(app_label)s' AND  ct.`model` = '%(model)s';
            ''' % {
                    'app_label':self.app_label, 'model': self.model, 'table': self.table, 
                    'cols_to': ', '.join(self.publishable_cols.keys()), 
                    'cols_from': ', '.join(self.publishable_cols.values())}
        )

        # add link to parent
        db.add_column(self.table, 'publishable_ptr_id', models.IntegerField(null=True))

        # update the link
        db.execute('''
            UPDATE
                `core_publishable` pub INNER JOIN `%(table)s` art ON (art.`id` = pub.`old_id`)
                SET
                    art.`publishable_ptr_id` = pub.`id`
            WHERE
                pub.`content_type_id` = (SELECT ct.`id` FROM `django_content_type` ct WHERE ct.`app_label` = '%(app_label)s' AND  ct.`model` = '%(model)s');
            ''' % {'app_label':self.app_label, 'model': self.model, 'table': self.table}
        )

        # TODO: we could use introspection to get the FK name in order to drop it
        # KUBA doda

        # replace it with a link to parent
        db.alter_column(self.table, 'publishable_ptr_id', models.ForeignKey(Publishable, primary_key=True))


    def backwards(self, orm):
        pass

    models = {}

    complete_apps = []

