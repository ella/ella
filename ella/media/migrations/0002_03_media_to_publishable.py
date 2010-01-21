
import datetime

from south.db import db
from django.db import models
from django.conf import settings

from ella.media.models import MediaField

from ella.core.migrations.base.base_0002 import BasePublishableDataMigration
from ella.core.migrations.base.base_0002 import alter_foreignkey_to_int, migrate_foreignkey


class Migration(BasePublishableDataMigration):
    # TODO:
    # this is only temporary, it should be constructed dynamically
    # from each migration in installed_apps, that contains run_before
    _depends_on = (
        ('jaknato.instruction', 'instruction', '0001_initial'),
    )
    depends_on = []
    for app, label, migration in _depends_on:
        if app in settings.INSTALLED_APPS:
            depends_on.append((label, migration))

    models = dict.copy(BasePublishableDataMigration.models)
    models.update(
        {
            'media.media': {
                'Meta': {'_bases': ['ella.core.models.publishable.Publishable']},
                'created': ('models.DateTimeField', ["_('Created')"], {'default': 'datetime.datetime.now', 'editable': 'False'}),
                'file': ('MediaField', [], {}),
                'publishable_ptr': ('models.OneToOneField', ["orm['core.Publishable']"], {}),
                'text': ('models.TextField', ["_('Content')"], {'blank': 'True'}),
                'updated': ('models.DateTimeField', ["_('Updated')"], {'null': 'True', 'blank': 'True'})
            },
        }
    )

    app_label = 'media'
    model = 'media'
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
        if 'jaknato.instruction' in settings.INSTALLED_APPS:
            # TODO: this should be solved via plugins
            alter_foreignkey_to_int('instruction_instruction', 'media')

    def move_self_foreignkeys(self, orm):
        # migrate authors as in base
        super(Migration, self).move_self_foreignkeys(orm)
        # migrate new media IDs to section
        migrate_foreignkey(self.app_label, self.model, 'media_section', self.model, self.orm)
        # migrate new media IDs to usage
        migrate_foreignkey(self.app_label, self.model, 'media_usage', self.model, self.orm)
        if 'jaknato.instruction' in settings.INSTALLED_APPS:
            # TODO: this should be solved via plugins
            migrate_foreignkey(self.app_label, self.model, 'instruction_instruction', self.model, self.orm)

