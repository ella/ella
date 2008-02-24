from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify

from ella.core.models import Listing, Category
from ella.core.cache import get_cached_object
from ella.photos.models import Photo

class Topic(models.Model):
    # ella fields
    slug = models.CharField(_('Slug'), db_index=True, max_length=255)
    category = models.ForeignKey(Category, verbose_name=_('Category'))

    photo = models.ForeignKey(Photo, blank=True, null=True, verbose_name=_('Photo'))
    created = models.DateTimeField(_('Created'), default=datetime.now, editable=False)

    title = models.CharField(_('Title'), max_length=255)
    description = models.TextField(_('Description'))

    def __unicode__(self):
        return self.title

    @property
    def main_listing(self):
        try:
            return get_cached_object(
                    Listing,
                    target_ct=ContentType.objects.get_for_model(self.__class__),
                    target_id=self.id,
                    category=self.category_id
)
        except Listing.DoesNotExist:
            return None

    def get_absolute_url(self):
        listing = self.main_listing
        if listing:
            return listing.get_absolute_url()

class Question(models.Model):
    topic = models.ForeignKey(Topic)
    slug = models.CharField(_('Slug'), db_index=True, max_length=255)

    title = models.CharField(_('Title'), max_length=255)
    description = models.TextField(_('Description'))

    # author if is authorized
    user = models.ForeignKey(User, verbose_name=_('authorized author'), blank=True, null=True)
    # author otherwise
    nickname = models.CharField(_("anonymous author's nickname"), max_length=255, blank=True)
    email = models.EmailField(_('authors email (optional)'), blank=True)

    # authors ip address
    ip_address = models.IPAddressField(_('ip address'), blank=True, null=True)

    created = models.DateTimeField(_('Created'), default=datetime.now, editable=False)
    is_public = models.BooleanField(_('is public'), default=True)

    def get_absolute_url(self):
        top = get_cached_object(Topic, pk=self.topic_id)
        return '%s%s/%s/' % (top.get_absolute_url(), slugify(ugettext('question')), self.slug)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')
        unique_together = (('topic', 'slug',),)
        ordering = ('-created',)

# initialization
from ella.discussions import register
del register

