
from south.db import db
from django.db import models
from ella.articles.models import *

from ella.core.migrations.basemigrations.publishable_data_migration import BasePublishableDataMigration

class Migration(BasePublishableDataMigration):

    app_label = 'series'
    model = 'serie'
    table = '%s_%s' % (app_label, model)

    publishable_uncommon_cols = {
        'description': 'description', # What about perex field??? there was description and perex fields together
    }
    
    def alter_self_foreignkeys(self, orm):
        alter_foreignkey_to_int('series_seriepart', 'serie')

    def move_self_foreignkeys(self, orm):
        # TODO: migrate new serie IDs to seriepart
