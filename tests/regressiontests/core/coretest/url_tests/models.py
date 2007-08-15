from django.db import models
from django.contrib.contenttypes.models import ContentType

from ella.core.models import Listing, Category

class SampleModel(models.Model):
    text = models.TextField()
    slug = models.CharField(_('Slug'), maxlength=255)
    category = models.ForeignKey(Category, verbose_name=_('Category'))

    @property
    def main_listing(self):
        return Listing.objects.get(
                target_ct=ContentType.objects.get_for_model(SampleModel),
                target_id=self.id,
                category=self.category
)

    def get_absolute_url(self):
        return self.main_listing.get_absolute_url()

class OtherSampleModel(models.Model):
    text = models.TextField()
    slug = models.CharField(_('Slug'), maxlength=255)
    category = models.ForeignKey(Category, verbose_name=_('Category'))

    @property
    def main_listing(self):
        return Listing.objects.get(
                target_ct=ContentType.objects.get_for_model(OtherSampleModel),
                target_id=self.id,
                category=self.category
)

    def get_absolute_url(self):
        return self.main_listing.get_absolute_url()

def register_urls():
    from ella.core.custom_urls import dispatcher
    from url_tests import views

    dispatcher.register('action', views.sample_view)
    dispatcher.register('otheraction', views.sample_view, model=OtherSampleModel)
