from datetime import datetime

from django.contrib.auth.models import User
from django.db import models

from nc.ratings.models import RatedManager

class UserProfile(models.Model):
    user = models.ForeignKey(User)
    karma = models.IntegerField(default=5)

class ExpensiveSampleModel(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(maxlength=100)

    objects = models.Manager()
    rated = RatedManager()

class CheapSampleModel(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(maxlength=100)

    objects = models.Manager()
    rated = RatedManager()
