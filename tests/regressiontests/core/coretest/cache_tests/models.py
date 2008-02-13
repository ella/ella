from django.db import models

class CachedModel(models.Model):
    title = models.CharField(max_length=100)
