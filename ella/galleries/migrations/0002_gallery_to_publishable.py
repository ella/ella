
from south.db import db
from django.db import models
from ella.galleries.models import *

from ella.core.migrations.base.base_0002 import BasePublishableDataMigration, alter_foreignkey_to_int

class Migration(BasePublishableDataMigration):

    app_label = 'galleries'
    model = 'gallery'
    table = '%s_%s' % (app_label, model)

    publishable_uncommon_cols = {
        'description': 'description',
    }
    
    def alter_self_foreignkeys(self, orm):
        # there is foreign key to authors called owner instead of ella's classic m2m rel
        alter_foreignkey_to_int('galleries_gallery', 'owner')
        alter_foreignkey_to_int('galleries_galleryitem', 'gallery')

    def move_self_foreignkeys(self, orm):
        pass
        # there is foreign key to authors called owner instead of ella's classic m2m rel
        # TODO: migrate new gallery IDs to core_publishable_authors
        # TODO: migrate new gallery IDs to galleryitem
