
import datetime

from south.db import db
from django.db import models
from django.utils.datastructures import SortedDict

from ella.core.migrations.base.base_0002 import BasePublishableDataMigration
from ella.core.migrations.base.base_0002 import alter_foreignkey_to_int, migrate_foreignkey


class Migration(BasePublishableDataMigration):
    models = dict.copy(BasePublishableDataMigration.models)
    models.update(
        {
            'galleries.gallery': {
                'Meta': {'_bases': ['ella.core.models.publishable.Publishable']},
                'content': ('models.TextField', ["_('Content')"], {'blank': 'True'}),
                'created': ('models.DateTimeField', ["_('Created')"], {'default': 'datetime.datetime.now', 'editable': 'False'}),
                'publishable_ptr': ('models.OneToOneField', ["orm['core.Publishable']"], {})
            },
        }
    )

    app_label = 'galleries'
    model = 'gallery'
    table = '%s_%s' % (app_label, model)

    publishable_uncommon_cols = {
        'description': 'description',
    }

    @property
    def publishable_cols(self):
        c = {
            'title': 'title',
            'slug': 'slug',
            'category_id': 'category_id',
        }
        c.update(self.publishable_uncommon_cols)
        return SortedDict(c)

    
    def alter_self_foreignkeys(self, orm):
        # there is foreign key to authors called owner instead of ella's classic m2m rel
        alter_foreignkey_to_int('galleries_gallery', 'owner')
        alter_foreignkey_to_int('galleries_galleryitem', 'gallery')

    def move_self_foreignkeys(self, orm):
        # there is foreign key to authors called owner instead of ella's classic m2m rel
        # TODO migrate new gallery IDs to core_publishable_authors
        #migrate_foreignkey(self.app_label, self.model, 'core_publishable_authors', 'publishable_id', self.orm)
        # migrate new gallery IDs to galleryitem
        db.delete_unique('galleries_galleryitem', ('gallery','order'))
        migrate_foreignkey(self.app_label, self.model, 'galleries_galleryitem', self.model, self.orm)
        db.create_unique('galleries_galleryitem', ('gallery_id','order'))

