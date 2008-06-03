from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType
from django.contrib.redirects.models import Redirect
from django.db.models import Model

from ella.core.cache import get_cached_object, get_cached_list
from ella.core.models import Placement, Category, HitCount
from ella.photos.models import Photo
from ella.ellaadmin.options import admin_url


class Publishable(object):
    """
    Abstract interface-like class that defines method's common to all objects that
    serve as primary content (can have a placement).
    """

    @property
    def main_placement(self):
        " Return object's main placement, that is the object's placement in its primary category "
        if not hasattr(self, '_main_placement'):
            try:
                # TODO - check and if we don't have category, take the only placement that exists in current site
                self._main_placement = get_cached_object(
                        Placement,
                        target_ct=ContentType.objects.get_for_model(self.__class__),
                        target_id=self.pk,
                        category=self.category_id
)
            except Placement.DoesNotExist:
                self._main_placement = None
        return self._main_placement

    def get_absolute_url(self):
        " Get object's URL. "
        placement = self.main_placement
        if placement:
            return placement.get_absolute_url()

    def get_admin_url(self):
        return admin_url(self)

    def save(self):
        if self.pk and hasattr(self, 'slug'): # only run on update
            # get old self
            old_self = self.__class__._default_manager.get(pk=self.pk)
            # the slug has changed
            if old_self.slug != self.slug:
                for plc in list(Placement.objects.filter(
                        target_id=self.pk,
                        target_ct=ContentType.objects.get_for_model(self.__class__)
).exclude(category=self.category_id)) + [self.main_placement]:
                    if plc.slug == old_self.slug:
                        plc.slug = self.slug
                        plc.save()
        return Model.save(self)

    def delete(self):
        url = self.get_absolute_url()
        Redirect.objects.filter(new_path=url).delete()
        return Model.delete(self)


    ##
    # various metadata
    ##
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

    def get_title(self):
        myTitle=self.title
        if myTitle:
           return '%s' % (self.title,)
        else:
           return '%s' % (self.draw_title(),)

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
            placement__target_ct=ContentType.objects.get_for_model(self.__class__),
            placement__target_id=self.id,
))
        return hits
    get_hits.short_description = _('Hit Counts')

    """
    def get_tags(self):
        from ella.tagging.models import TaggedItem
    """
