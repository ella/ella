from django.db import models
from django.contrib import admin

class DbTemplate(models.Model):
    name = models.CharField(_('Name'), maxlength=200, primary_key=True)
    description = models.CharField(_('Description'), maxlength=500, blank=True)
    text = models.TextField(_('Definition'))

    class Meta:
        ordering = ('name',)

class DbTemplateOptions(admin.ModelOptions):
    pass

admin.site(DbTemplate, DbTemplateOptions)
