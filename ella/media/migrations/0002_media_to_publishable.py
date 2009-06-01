
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
        'description': 'description',
    }

    def alter_self_foreignkeys(self, orm):
        # migrate authors as in base
        super(Migration, self).alter_self_foreignkeys(orm)
        alter_foreignkey_to_int('media_section', 'media')
        alter_foreignkey_to_int('media_usage', 'media')

    def move_self_foreignkeys(self, orm):
        # migrate authors as in base
        super(Migration, self).move_self_foreignkeys(orm)
        # TODO: migrate new media IDs to section
        # TODO: migrate new media IDs to usage

