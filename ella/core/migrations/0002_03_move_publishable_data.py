
from south.db import db
from django.db import models

class Migration:

    # TODO:
    # this is only temporary, it should be constructed dynamically
    # from each migration in installed_apps, that contains run_before
    depends_on = (
        ('articles', '0002_03_move_article_data'),
        ('galleries', '0002_03_gallery_to_publishable'),
        ('interviews'), ('0002_03_interview_to_publishable'),
        ('media'), ('0002_03_media_to_publishable'),
        ('polls'), ('0002_03_01_contest_to_publishable'),
        ('polls'), ('0002_03_02_quiz_to_publishable'),
        ('series'), ('0002_03_serie_to_publishable'),
        ('discussions'), '0002_03_move_topic_data'),
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


