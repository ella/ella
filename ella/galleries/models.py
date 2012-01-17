from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import SortedDict

from ella.core.models import Publishable
from ella.core.cache.utils import cache_this
from ella.core.custom_urls import resolver
from ella.photos.models import Photo


def get_gallery_key(func, gallery):
    return 'ella.galleries.models.Gallery.items:%d' % gallery.id

class Gallery(Publishable):
    """
    Definition of objects gallery
    """
    # Gallery metadata
    content = models.TextField(_('Content'), blank=True)
    created = models.DateTimeField(_('Created'), default=datetime.now, editable=False)


    def get_text(self):
        return self.content

    @property
    def items(self):
        """
        Returns sorted dict of gallery items. Unique items slugs are used as keys.
        Values are tuples of items and their targets.
        """
        if self.id:
            return self._get_gallery_items()
        return SortedDict()

    @cache_this(get_gallery_key)
    def _get_gallery_items(self):
        """
        Returns sorted dict of gallery items. Unique items slugs are used as keys.
        """
        return SortedDict((item.photo.slug, item) for item in self.galleryitem_set.all())

    class Meta:
        verbose_name = _('Gallery')
        verbose_name_plural = _('Galleries')


class GalleryItem(models.Model):
    """
    Specific object in gallery
    """
    gallery = models.ForeignKey(Gallery, verbose_name=_("Parent gallery"))
    photo = models.ForeignKey(Photo, verbose_name=_("Photo"))
    order = models.IntegerField(_('Object order')) # TODO: order with respect to
    text = models.TextField(blank=True)

    def __unicode__(self):
        return u"%s %s %s %s" % (self.photo, _('in gallery'), self.gallery.title)

    def get_absolute_url(self):
        if self.order == 0:
            return self.gallery.get_absolute_url()
        return resolver.reverse(self.gallery, 'gallery-item-detail', self.photo.slug)

    class Meta:
        ordering = ('order', )
        verbose_name = _('Gallery item')
        verbose_name_plural = _('Gallery items')
        unique_together = (('gallery', 'order',),)

