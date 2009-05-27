
from south.db import db
from django.db import models
from ella.articles.models import *

from ella.core.migrations.basemigrations.publishable_data_migration import BasePublishableDataMigration

class Migration(BasePublishableDataMigration):

    APP = 'articles'
    MODEL = 'article'
    TABLE = '%s_%s' % (APP, MODEL)

    PUBLISHABLE_UNCOMMON_COLS = {
        'description': 'perex',
    }
