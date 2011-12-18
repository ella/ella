
from south.db import db
from django.db import models
from django.conf import settings

class Migration:

    pass

    # TODO:
    # this is only temporary, it should be constructed dynamically
    # from each migration in installed_apps, that contains run_before
#    _depends_on = (
#        ('ella.articles', 'articles', '0002_03_move_article_data'),
#        ('ella.galleries', 'galleries', '0002_03_gallery_to_publishable'),
#        ('ella.interviews', 'interviews', '0002_03_interview_to_publishable'),
#        ('ella.polls', 'polls', '0002_03_01_contest_to_publishable'),
#        ('ella.polls', 'polls', '0002_03_02_quiz_to_publishable'),
#        ('ella.series', 'series', '0002_03_serie_to_publishable'),
#        ('ella.discussions', 'discussions', '0002_03_move_topic_data'),
#        ('recepty.recipes', 'recipes', '0002_03_recipe_to_publishable'),
#        ('jaknato.instruction', 'instruction', '0002_03_move_instruction_data'),
#        ('stdout.events', 'events', '0002_03_move_publishable_data'),
#    )
#    depends_on = []
#    for app, label, migration in _depends_on:
#        if app in settings.INSTALLED_APPS:
#            depends_on.append((label, migration))
#
    def forwards(self, orm):
        print 'running all dependencies'
#
    def backwards(self, orm):
        print 'there is no way back'
#
#    models = {
#        'core.publishable': {
#            'Meta': {'app_label': "'core'"},
#            '_stub': True,
#            'id': ('models.AutoField', [], {'primary_key': 'True'})
#        },
#    }

