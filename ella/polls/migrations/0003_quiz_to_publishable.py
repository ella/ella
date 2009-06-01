
from south.db import db
from django.db import models
from ella.polls.models import *

from ella.core.migrations_base import BasePublishableDataMigration, alter_foreignkey_to_int

class Migration(BasePublishableDataMigration):

    app_label = 'polls'
    model = 'quiz'
    table = '%s_%s' % (app_label, model)

    publishable_uncommon_cols = {}
    
    def alter_self_foreignkeys(self, orm):
        # migrate authors as in base
        super(Migration, self).alter_self_foreignkeys(orm)
        alter_foreignkey_to_int('polls_question', 'quiz')
        alter_foreignkey_to_int('polls_results', 'quiz')

    def move_self_foreignkeys(self, orm):
        # migrate authors as in base
        super(Migration, self).move_self_foreignkeys(orm)
        # TODO: migrate new quiz IDs to question
        # TODO: migrate new quiz IDs to results
