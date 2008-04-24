from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from ella.core.models import Listing, Category
from ella.db.models import Publishable

class SampleModel(models.Model, Publishable):
    text = models.TextField()
    slug = models.CharField(_('Slug'), max_length=255)
    category = models.ForeignKey(Category, verbose_name=_('Category'))

class OtherSampleModel(models.Model, Publishable):
    text = models.TextField()
    slug = models.CharField(_('Slug'), max_length=255)
    category = models.ForeignKey(Category, verbose_name=_('Category'))

def register_urls():
    from ella.core.custom_urls import dispatcher
    from url_tests import views

    dispatcher.register('action', views.sample_view)
    dispatcher.register('otheraction', views.sample_view, model=OtherSampleModel)
