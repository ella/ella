
from south.db import db
from django.db import models
from ella.interviews.models import *

from ella.core.migrations.base.base_0002 import BasePublishableDataMigration, alter_foreignkey_to_int

class Migration(BasePublishableDataMigration):

    app_label = 'interviews'
    model = 'interview'
    table = '%s_%s' % (app_label, model)

    publishable_uncommon_cols = {
        'source_id': 'source_id',
        'description': 'perex',
    }
    
    def alter_self_foreignkeys(self, orm):
        alter_foreignkey_to_int('interviews_question', 'interview')
        alter_foreignkey_to_int('interviews_interview_interviewees', 'interview')

    def move_self_foreignkeys(self, orm):
        pass
        # TODO: migrate new article IDs to question
        # TODO: migrate new article IDs to interview_interviewees
