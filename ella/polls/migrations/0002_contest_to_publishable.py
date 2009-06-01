
from south.db import db
from django.db import models
from ella.articles.models import *

from ella.core.migrations.basemigrations.publishable_data_migration import BasePublishableDataMigration

class Migration(BasePublishableDataMigration):

    app_label = 'polls'
    model = 'contest'
    table = '%s_%s' % (app_label, model)

    publishable_uncommon_cols = {}
    
    def alter_self_foreignkeys(self, orm):
        alter_foreignkey_to_int('polls_question', 'contest')
        alter_foreignkey_to_int('polls_contestant', 'contest')

    def move_self_foreignkeys(self, orm):
        # TODO: migrate new contest IDs to question
        # TODO: migrate new contest IDs to contestant
