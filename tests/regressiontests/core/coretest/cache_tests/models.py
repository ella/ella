from django.db import models

class CachedModel(models.Model):
    title = models.CharField(maxlength=100)
