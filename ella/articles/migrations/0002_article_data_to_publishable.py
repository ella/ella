
from south.db import db
from django.db import models
from ella.articles.models import *

from ella.core.migrations.basemigrations.publishable_data_migration import BasePublishableDataMigration

class Migration(BasePublishableDataMigration):

    app_label = 'articles'
    model = 'article'
    table = '%s_%s' % (app_label, model)

    publishable_uncommon_cols = {
        'source_id': 'source_id', 
        'description': 'perex',
    }
