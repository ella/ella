from django.db import models
from django.contrib import admin

from ella.db.models import Publishable
from ella.core.models import Category
from ella.core.admin import PlacementInlineOptions

class SampleAdminObject(Publishable, models.Model):
    slug = models.CharField(max_length=100)
    category = models.ForeignKey(Category)

class EmptyAdminObject(Publishable, models.Model):
    content = models.TextField()

class SampleAdminObjectOptions(admin.ModelAdmin):
    inlines = (PlacementInlineOptions,)

admin.site.register([SampleAdminObject, EmptyAdminObject, ], SampleAdminObjectOptions)
