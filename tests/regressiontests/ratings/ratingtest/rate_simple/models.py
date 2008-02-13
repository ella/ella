from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models

from ella.ratings.models import RatedManager, INITIAL_USER_KARMA
from ella.core.models import Category, Listing

class UserProfile(models.Model):
    user = models.ForeignKey(User)
    karma = models.IntegerField(default=INITIAL_USER_KARMA)
    karma_coeficient = models.FloatField(default=1.0)

class ExpensiveSampleModel(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(max_length=100)
    category = models.ForeignKey(Category)
    slug = models.CharField(max_length=100)

    objects = models.Manager()
    rated = RatedManager()

    @property
    def main_listing(self):
        return Listing.objects.get(
                target_ct=ContentType.objects.get_for_model(ExpensiveSampleModel),
                target_id=self.id,
                category=self.category
)

    def get_absolute_url(self):
        return self.main_listing.get_absolute_url()


class CheapSampleModel(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(max_length=100)

    objects = models.Manager()
    rated = RatedManager()
