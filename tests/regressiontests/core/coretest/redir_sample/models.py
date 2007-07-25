from django.db import models
from django.contrib.contenttypes.models import ContentType

from ella.core.models import Category, Listing

class RedirObject(models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(maxlength=100)
    slug =  models.CharField(maxlength=100)

    @property
    def main_listing(self):
        return Listing.objects.get(
                target_ct=ContentType.objects.get_for_model(RedirObject),
                target_id=self.id,
                category=self.category
)

    def get_absolute_url(self):
        return self.main_listing.get_absolute_url()

