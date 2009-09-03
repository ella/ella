
from south.db import db
from django.db import models

from ella.core.migrations.base.base_0002 import BasePublishableDataMigration
from ella.core.migrations.base.base_0002 import alter_foreignkey_to_int, migrate_foreignkey


class Migration(BasePublishableDataMigration):
    models = dict.copy(BasePublishableDataMigration.models)
    models.update(
        {
            'interviews.interview': {
                'Meta': {'ordering': "('-ask_from',)", '_bases': ['ella.core.models.publishable.Publishable']},
                'ask_from': ('models.DateTimeField', ["_('Ask from')"], {}),
                'ask_to': ('models.DateTimeField', ["_('Ask to')"], {}),
                'content': ('models.TextField', ["_('Text')"], {}),
                'interviewees': ('models.ManyToManyField', ["orm['interviews.Interviewee']"], {'verbose_name': "_('Interviewees')"}),
                'publishable_ptr': ('models.OneToOneField', ["orm['core.Publishable']"], {}),
                'reply_from': ('models.DateTimeField', ["_('Reply from')"], {}),
                'reply_to': ('models.DateTimeField', ["_('Reply to')"], {}),
                'upper_title': ('models.CharField', ["_('Upper title')"], {'max_length': '255', 'blank': 'True'})
            },
            'interviews.interviewee': {
                'Meta': {'ordering': "('name',)"},
                'author': ('models.ForeignKey', ["orm['core.Author']"], {'null': 'True', 'blank': 'True'}),
                'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
                'id': ('models.AutoField', [], {'primary_key': 'True'}),
                'name': ('models.CharField', ["_('Name')"], {'max_length': '200', 'blank': 'True'}),
                'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
                'user': ('models.ForeignKey', ["orm['auth.User']"], {'null': 'True', 'blank': 'True'})
            },
            'auth.user': {
                '_stub': True,
                'id': ('models.AutoField', [], {'primary_key': 'True'})
            },
            'core.author': {
                'Meta': {'app_label': "'core'"},
                '_stub': True,
                'id': ('models.AutoField', [], {'primary_key': 'True'})
            },
        }
    )

    app_label = 'interviews'
    model = 'interview'
    table = '%s_%s' % (app_label, model)

    publishable_uncommon_cols = {
        'source_id': 'source_id',
        'description': 'perex',
    }
    
    def alter_self_foreignkeys(self, orm):
        # migrate authors as in base
        super(Migration, self).alter_self_foreignkeys(orm)
        alter_foreignkey_to_int('interviews_question', 'interview')
        alter_foreignkey_to_int('interviews_interview_interviewees', 'interview')

    def move_self_foreignkeys(self, orm):
        # migrate authors as in base
        super(Migration, self).move_self_foreignkeys(orm)
        # migrate new article IDs to question
        migrate_foreignkey(self.app_label, self.model, 'interviews_question', self.model, self.orm)
        # migrate new article IDs to interview_interviewees
        migrate_foreignkey(self.app_label, self.model, 'interviews_interview_interviewees', self.model, self.orm)

