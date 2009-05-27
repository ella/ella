
from south.db import db
from django.db import models
from django.utils.datastructures import SortedDict

from ella.core.models import *


class BasePublishableDataMigration:

    depends_on = (
        ("core", "0001_initial"), # TODO publishable mig
    )

    APP = ''
    MODEL = ''
    TABLE = '%s_%s' % (APP, MODEL)

    _PUBLISHABLE_DEFAULT_COLS = {
        'title': 'title',
        'slug': 'slug',
        'category_id': 'category_id', 
        'source_id': 'source_id', 
        'photo_id': 'photo_id', 
        'description': 'description',
    }

    PUBLISHABLE_UNCOMMON_COLS = {}

    @property
    def publishanle_cols(self):
        c = self._PUBLISHABLE_DEFAULT_COLS.copy()
        c.update(**self.PUBLISHABLE_UNCOMMON_COLS)
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
                    ct.`app_label` = '%(app)s' AND  ct.`model` = '%(model)s';
            ''' % {
                    'app':self.APP, 'model': self.MODEL, 'table': self.TABLE, 
                    'cols_to': ', '.join(self.publishanle_cols.keys()), 
                    'cols_from': ', '.join(self.publishanle_cols.values())}
        )

        # add link to parent
        db.add_column(self.TABLE, 'publishable_ptr_id', models.IntegerField(null=True))

        # update the link
        db.execute('''
            UPDATE
                `core_publishable` pub INNER JOIN `%(table)s` art ON (art.`id` = pub.`old_id`)
                SET
                    art.`publishable_ptr_id` = pub.`id`
            WHERE
                pub.`content_type_id` = (SELECT ct.`id` FROM `django_content_type` ct WHERE ct.`app_label` = '%(app)s' AND  ct.`model` = '%(model)s');
            ''' % {'app':self.APP, 'model': self.MODEL, 'table': self.TABLE}
        )

        # TODO: we could use introspection to get the FK name in order to drop it
        # KUBA doda

        # replace it with a link to parent
        db.alter_column(self.TABLE, 'publishable_ptr_id', models.ForeignKey(Publishable, primary_key=True))


    def backwards(self, orm):
        pass

    models = {}

    complete_apps = []

