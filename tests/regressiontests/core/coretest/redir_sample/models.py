from django.db import models

from ella.core.models import Category
from ella.db.models import Publishable

class RedirObject(Publishable, models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=100)
    slug =  models.CharField(max_length=100)

