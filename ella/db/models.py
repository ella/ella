from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType

from ella.core.cache import get_cached_object, get_cached_list
from ella.core.models import Listing, Category, HitCount
from ella.photos.models import Photo
from ella.ellaadmin.options import admin_url


class Publishable(object):
    """
    Abstract interface-like class that defines method's common to all objects that
    serve as primary content (can have a listing).
    """

    @property
    def main_listing(self):
        " Return object's main listing, that is the object's listing in its primary category "
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
        " Get object's URL. "
        listing = self.main_listing
        if listing:
            return listing.get_absolute_url()

    def get_admin_url(self):
        return admin_url(self)

    def get_category(self):
        " Get object's primary Category."
        return get_cached_object(Category, pk=self.category_id)


    def get_photo(self):
        " Get object's Photo. "
        if not hasattr(self, '_photo'):
            try:
                self._photo = get_cached_object(Photo, pk=self.photo_id)
            except Photo.DoesNotExist:
                self._photo = None
        return self._photo

    def get_description(self):
        return self.description


    ##
    # Custom admin fields
    ##
    def full_url(self):
        absolute_url = self.get_absolute_url()
        if absolute_url:
            return mark_safe('<a href="%s">url</a>' % absolute_url)
        return 'no url'
    full_url.allow_tags = True

    def photo_thumbnail(self):
        photo = self.get_photo()
        if photo:
            return mark_safe(photo.thumb())
        else:
            return mark_safe('<div class="errors"><ul class="errorlist"><li>%s</li></ul></div>' % ugettext('No main photo!'))
    photo_thumbnail.allow_tags = True

    def get_hits(self):
        # there can be more hitcounts for various sites
        hits = sum(i.hits for i in get_cached_list(HitCount,
            target_ct=ContentType.objects.get_for_model(self.__class__),
            target_id=self.id,
))
        return hits
    get_hits.short_description = _('Hit Counts')

