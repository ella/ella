
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
        alter_foreignkey_to_int('articles_articlecontents', 'article')
        # TODO: migrate new article IDs to articlecontents
        alter_foreignkey_to_int('recipes_oldrecipearticleredirect', 'new_id')
        # TODO: migrate new article IDs to oldrecipearticleredirect

