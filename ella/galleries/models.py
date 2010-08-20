from datetime import datetime

from django.db import models
from django.http import Http404
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import SortedDict

from ella.core.models import Publishable
from ella.core.cache.utils import cache_this, CachedGenericForeignKey
from ella.core.cache.invalidate import CACHE_DELETER
from ella.core.custom_urls import resolver
from ella.photos.models import Photo


def gallery_cache_invalidator(key, gallery, *args, **kwargs):
    """Registers gallery cache invalidator test in the cache system."""
    CACHE_DELETER.register_pk(gallery, key)
    CACHE_DELETER.register_test(GalleryItem, 'gallery_id:%s' % gallery.pk, key)

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

    @cache_this(get_gallery_key, gallery_cache_invalidator)
    def _get_gallery_items(self):
        """
        Returns sorted dict of gallery items. Unique items slugs are used as keys.
        Values are tuples of items and their targets.
        """
        slugs_count = {}
        itms = [ (item, item.target) for item in self.galleryitem_set.all() ]
        slugs_unique = set((i[1].slug for i in itms))
        res = SortedDict()

        for item, target in itms:
            slug = target.slug
            if slug not in slugs_count:
                slugs_count[slug] = 1
                res[slug] = (item, target)
            else:
                while "%s%s" % (slug, slugs_count[slug]) in slugs_unique:
                    slugs_count[slug] += 1
                new_slug = "%s%s" % (slug, slugs_count[slug])
                slugs_unique.add(new_slug)
                res[new_slug] = (item, target)
        return res

    def get_photo(self):
        """
        Returns first Photo item in the gallery if no photo is set on self.photo.

        Overrides Publishable.get_photo.
        """
        photo = self.photo
        if photo is not None:
            return photo

        for item in self.items.itervalues():
            if isinstance(item[1], Photo):
                return item[1]

    def assign_photo(self):
        if not self.pk:
            return
        if self.photo is None:
            first_photo = self.get_photo()
            if first_photo:
                self.photo = first_photo
                self.save()

    class Meta:
        verbose_name = _('Gallery')
        verbose_name_plural = _('Galleries')


class GalleryItem(models.Model):
    """
    Specific object in gallery
    """
    gallery = models.ForeignKey(Gallery, verbose_name=_("Parent gallery"))
    target_ct = models.ForeignKey(ContentType, verbose_name=_('Target content type'))
    target_id = models.IntegerField(_('Target ID'), db_index=True)
    order = models.IntegerField(_('Object order')) # TODO: order with respect to

    target = CachedGenericForeignKey(ct_field="target_ct", fk_field="target_id")

    def __unicode__(self):
        return u"%s %s %s %s" % (_(self.target_ct.name), self.target, _('in gallery'), self.gallery.title)

    def _get_slug(self):
        if not hasattr(self, '_item_list'):
            self._item_list = self.gallery.items

        for slug, item in self._item_list.items():
            if item[0] == self:
                return slug
        else:
            raise Http404

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
        ordering = ('order',)
        verbose_name = _('Gallery item')
        verbose_name_plural = _('Gallery items')
        unique_together = (('gallery', 'order',),)

