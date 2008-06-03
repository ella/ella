from django.db import models
from django.contrib import admin
from ella.db.models import Publishable
from ella.core.models import Category

class Something(models.Model):
    description = models.CharField(max_length=200)
    title = models.CharField(max_length=50)

    def __unicode__(self):
        return '%s: %s...' % (self.title, self.description[:20])

class IchBinLadin(Publishable, models.Model):
    organisation = models.CharField(max_length=50)
    category  = models.ForeignKey(Category) # publishable son has to declare foreignkey to category! (dig why it couldn't be inherited in qsrf?)

    def __unicode__(self):
        return self.organisation

