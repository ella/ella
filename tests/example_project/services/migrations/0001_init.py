
from south.db import db
from django.db import models
from example_project.services.models import *

class Migration:

    depends_on = (
        ("core", "0002_add_author_email"),
    )

    def forwards(self, orm):
        "Write your forwards migration here"


    def backwards(self, orm):
        "Write your backwards migration here"


    models = {

    }


