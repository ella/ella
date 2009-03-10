from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site

from ella.core.cache import get_cached_object, get_cached_list
from ella.core.models.main import Category, Author, Source, Placement
from ella.photos.models import Photo
from django.conf import settings

class Publishable(models.Model):
    """
    Base class for all object that can be published in ella
    """
    content_type = models.ForeignKey(ContentType)

    category = models.ForeignKey(Category, verbose_name=_('Category'))

    # Titles
    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=255)

    # Authors and Sources
    authors = models.ManyToManyField(Author, verbose_name=_('Authors'))
    source = models.ForeignKey(Source, blank=True, null=True, verbose_name=_('Source'))

    # Main Photo
    photo = models.ForeignKey(Photo, blank=True, null=True, verbose_name=_('Photo'))

    # Description
    description = models.TextField(_('Description'))

    class Meta:
        app_label = 'core'

    @property
    def target(self):
        if not hasattr(self, '_target'):
            self._target = self.content_type.get_object_for_this_type(pk=self.pk)
        return self._target

    placements = generic.GenericRelation(Placement, object_id_field='target_id', content_type_field='target_ct')

    if 'ella.comments' in settings.INSTALLED_APPS:
        from ella.comments.models import Comment
        comments = generic.GenericRelation(Comment, object_id_field='target_id', content_type_field='target_ct')

    if 'ella.tagging' in settings.INSTALLED_APPS:
        from ella.tagging.models import TaggedItem
        tags = generic.GenericRelation(TaggedItem)

    @property
    def main_placement(self):
        " Return object's main placement, that is the object's placement in its primary category "
        if hasattr(self, '_main_placement'):
            return self._main_placement

        current_site = Site.objects.get_current()

        # TODO: what if have got multiple listings on one site?
        placements = get_cached_list(
                Placement,
                target_ct=ContentType.objects.get_for_model(self.__class__),
                target_id=self.pk,
                category__site=current_site,
            )
        if placements:
            return placements[0]

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

    def get_absolute_url(self, domain=False):
        " Get object's URL. "
        placement = self.main_placement
        if placement:
            return placement.get_absolute_url(domain=domain)

    def get_domain_url(self):
        return self.get_absolute_url(domain=True)

    def get_admin_url(self):
        from ella.ellaadmin.utils import admin_url
        return admin_url(self)

    def save(self, force_insert=False, force_update=False):
        self.content_type = ContentType.objects.get_for_model(self)
        if self.pk and hasattr(self, 'slug'): # only run on update
            # get old self
            old_slug = self.__class__._default_manager.get(pk=self.pk).slug
            # the slug has changed
            if old_slug != self.slug:
                for plc in Placement.objects.filter(
                        target_id=self.pk,
                        target_ct=ContentType.objects.get_for_model(self.__class__)
                    ):
                    if plc.slug == old_slug:
                        plc.slug = self.slug
                        plc.save(force_update=True)
        return super(Publishable, self).save(force_insert, force_update)

    def delete(self):
        url = self.get_absolute_url()
        Redirect.objects.filter(new_path=url).delete()
        return super(Publishable, self).delete()


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

    def get_text(self):
        return self.text



