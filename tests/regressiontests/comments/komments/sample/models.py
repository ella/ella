from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from ella.core.models import Listing, Category

class Apple(models.Model):
    color = models.CharField(max_length=20)

    def __unicode__(self):
        return u'%s apple' % (self.color,)
    def get_absolute_url(self):
        return u'/sample/list/apples/%s/' % self.color

class Orange(models.Model):
    cm = models.PositiveIntegerField()
    slug = models.CharField(_('Slug'), max_length=255)
    category = models.ForeignKey(Category, verbose_name=_('Category'))

    @property
    def main_listing(self):
        return Listing.objects.get(
                target_ct=ContentType.objects.get_for_model(Orange),
                target_id=self.id,
                category=self.category
)

    def get_absolute_url(self):
        return self.main_listing.get_absolute_url()

    def __unicode__(self):
        return u'%scm orange' % (self.cm,)


from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

admin.site.register(Apple)
admin.site.register(Orange)

