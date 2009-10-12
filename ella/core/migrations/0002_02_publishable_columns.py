
from south.db import db
from django.db import models

class Migration:

    def forwards(self, orm):
        # add a temporary column on core_publishable to remember the old ID
        db.add_column('core_publishable', 'old_id', models.IntegerField(null=True))

        #FIXME: add helper index needed at least during migration (tonda)
        db.create_index('core_publishable', ['content_type_id', 'old_id'])

        # column for new foreign keys to publishable
        db.add_column('core_placement', 'publishable_id', models.IntegerField(null=True))

        # Adding field 'Author.email'
        db.add_column('core_author', 'email', models.EmailField(_('Email'), blank=True))

        # Adding field 'Listing.publish_to'
        db.add_column('core_listing', 'publish_to', models.DateTimeField(_("End of listing"), null=True, blank=True))
        db.delete_column('core_listing', 'remove')

    def backwards(self, orm):

        # drop temporary column
        db.delete_column('core_publishable', 'old_id')

        # drop publishable foreign key
        db.delete_column('core_placement', 'publishable_id')

        # Deleting field 'Author.email'
        db.delete_column('core_author', 'email')

        # Deleting field 'Listing.publish_to'
        db.delete_column('core_listing', 'publish_to')

    models = {
        'core.publishable': {
            'Meta': {'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
    }

