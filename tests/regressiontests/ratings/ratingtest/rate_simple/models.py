from datetime import datetime
from django.contrib.auth.models import User
from django.db import models

from ella.ratings.models import RatedManager, INITIAL_USER_KARMA

class UserProfile(models.Model):
    user = models.ForeignKey(User)
    karma = models.IntegerField(default=INITIAL_USER_KARMA)
    karma_coeficient = models.FloatField(default=1.0)

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
