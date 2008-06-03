from django.db import models
from django.contrib import admin

class Something(models.Model):
    description = models.CharField(max_length=200)
    title = models.CharField(max_length=50)

    def __unicode__(self):
        return '%s: %s...' % (self.title, self.description[:20])

class IchBinLadin(models.Model):
    organisation = models.CharField(max_length=50)

    def __unicode__(self):
        return self.organisation

