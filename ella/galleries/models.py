from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import SortedDict

from ella.core.models import Publishable
from ella.core.cache import cache_this, CachedForeignKey
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
        Values are tuples of items and their targets.
        """
        slugs_count = {}
        itms = [ (item, item.photo) for item in self.galleryitem_set.all() ]
        slugs_unique = set((i[1].slug for i in itms))
        res = SortedDict()

        for item, target in itms:
            # poor man's identity mapper
            item.gallery = self
            slug = target.slug
            if slug not in slugs_count:
                slugs_count[slug] = 1
                res[slug] = item
            else:
                while "%s%s" % (slug, slugs_count[slug]) in slugs_unique:
                    slugs_count[slug] += 1
                new_slug = "%s%s" % (slug, slugs_count[slug])
                slugs_unique.add(new_slug)
                res[new_slug] = item
        return res

    class Meta:
        verbose_name = _('Gallery')
        verbose_name_plural = _('Galleries')


class GalleryItem(models.Model):
    """
    Specific object in gallery
    """
    gallery = models.ForeignKey(Gallery, verbose_name=_("Parent gallery"))
    photo = CachedForeignKey(Photo, verbose_name=_("Photo"))
    order = models.IntegerField(_('Object order')) # TODO: order with respect to

    title = models.CharField(_('Title'), max_length=255, blank=True)
    text = models.TextField(blank=True)

    def __unicode__(self):
        return u"%s %s %s %s" % (self.photo, _('in gallery'), self.gallery.title)

    def _get_slug(self):
        for slug, item in self.gallery.items.items():
            if item == self:
                return slug

    def get_slug(self):
        """
        Return a unique slug for given gallery, even if there are more objects with the same slug.
        """
        if not hasattr(self, '_slug'):
            self._slug = self._get_slug()
        return self._slug

    def get_absolute_url(self):
        if self.order == 0:
            return self.gallery.get_absolute_url()
        return resolver.reverse(self.gallery, 'gallery-item-detail', self.get_slug())

    class Meta:
        ordering = ('order', )
        verbose_name = _('Gallery item')
        verbose_name_plural = _('Gallery items')
        unique_together = (('gallery', 'order',),)

