
from south.db import db
from django.db import models

class Migration:

    # TODO:
    # this is only temporary, it should be constructed dynamically
    # from each migration in installed_apps, that contains run_before
    depends_on = (
        ('articles', '0002_03_move_article_data'),
    )

    def forwards(self, orm):
        print 'running all dependencies'

    def backwards(self, orm):
        print 'there is no way back'

    models = {
        'core.publishable': {
            'Meta': {'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
    }


