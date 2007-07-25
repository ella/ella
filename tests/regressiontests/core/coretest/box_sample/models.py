from django.db import models

from ella.core.box import Box

class BoxedObject(models.Model):
    title = models.CharField(maxlength=100)
    description = models.TextField()

    def Box(self, box_type, nodelist):
        return Box(self, box_type, nodelist)

class UnBoxedObject(models.Model):
    title = models.CharField(maxlength=100)
    description = models.TextField()
