from datetime import datetime

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.contrib.redirects.models import Redirect

from ella.ellaadmin.utils import admin_url
from ella.core.managers import ListingManager, HitCountManager, PlacementManager
from ella.core.cache import get_cached_object, get_cached_list
from ella.core.models.main import Category, Author, Source
from ella.photos.models import Photo
from ella.core.box import Box

def PublishableBox(publishable, box_type, nodelist, model=None):
    "add some content type info of self.target"
    if not model:
        model = publishable.content_type.model_class()
    box_class = model.box_class

    if box_class == PublishableBox:
        box_class = Box
    return box_class(publishable, box_type, nodelist, model=model)

class Publishable(models.Model):
    """
    Base class for all object that can be published in ella
    """
    box_class = staticmethod(PublishableBox)

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

    if 'ella.comments' in settings.INSTALLED_APPS:
        from ella.comments.models import Comment
        comments = generic.GenericRelation(Comment, object_id_field='target_id', content_type_field='target_ct')

    @property
    def main_placement(self):
        " Return object's main placement, that is the object's placement in its primary category "
        if hasattr(self, '_main_placement'):
            return self._main_placement

        current_site = Site.objects.get_current()

        # TODO: what if have got multiple listings on one site?
        placements = get_cached_list(
                Placement,
                publishable=self.pk,
                category__site=current_site,
            )
        if placements:
            if len(placements) == 1:
                return placements[0]
            else:
                # with multiple listings, one with first publish_from
                # primary
                first_published = None
                for placement in placements:
                    if first_published is None or placement.publish_from < first_published.publish_from:
                        first_published = placement

                assert first_published is not None
                return first_published


        try:
            # TODO - check and if we don't have category, take the only placement that exists in current site
            self._main_placement = get_cached_object(
                    Placement,
                    publishable=self.pk,
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
        return admin_url(self)

    def save(self, force_insert=False, force_update=False):
        self.content_type = ContentType.objects.get_for_model(self)
        if self.pk and hasattr(self, 'slug'): # only run on update
            # get old self
            old_slug = self.__class__._default_manager.get(pk=self.pk).slug
            # the slug has changed
            if old_slug != self.slug:
                for plc in Placement.objects.filter(publishable=self):
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

    def __unicode__(self):
        return self.get_title()

# FIXME find another way to register!
if 'tagging' in settings.INSTALLED_APPS:
    import tagging
    tagging.register(Publishable)


class Placement(models.Model):
    # listing's target - a Publishable object
    publishable = models.ForeignKey(Publishable)
    category = models.ForeignKey(Category, db_index=True)
    publish_from = models.DateTimeField(_("Start of visibility")) #, default=datetime.now)
    publish_to = models.DateTimeField(_("End of visibility"), null=True, blank=True)
    slug = models.SlugField(_('Slug'), max_length=255, blank=True)

    static = models.BooleanField(default=False)

    objects = PlacementManager()

    class Meta:
        app_label = 'core'
        verbose_name = _('Placement')
        verbose_name_plural = _('Placements')

    def __unicode__(self):
        try:
            return u'%s placed in %s' % (self.publishable, self.category)
        except:
            return 'Broken placement'

    def is_active(self):
        "Return True if the listing's priority is currently active."
        now = datetime.now()
        return now > self.publish_from and (self.publish_to is None or now < self.publish_to)

    def save(self, force_insert=False, force_update=False):
        " If Listing is created, we create HitCount object "

        if not self.slug:
            self.slug = self.publishable.slug

        if self.pk:
            old_self = Placement.objects.get(pk=self.pk)

            old_path = old_self.get_absolute_url()
            new_path = self.get_absolute_url()

            if old_path != new_path and new_path:
                redirect, created = Redirect.objects.get_or_create(old_path=old_path, new_path=new_path, defaults={'site_id' : self.category.site_id})
                Redirect.objects.filter(new_path=old_path).exclude(pk=redirect.pk).update(new_path=new_path)

        # First, save Placement
        super(Placement, self).save(force_insert, force_update)
        # Then, save HitCount (needs placement_id)
        hc, created = HitCount.objects.get_or_create(placement=self)

    def get_absolute_url(self, domain=False):
        obj = self.publishable
        category = get_cached_object(Category, pk=self.category_id)

        kwargs = {
            'content_type' : slugify(obj.content_type.model_class()._meta.verbose_name_plural),
            'slug' : self.slug,
        }

        if self.static:
            if category.tree_parent_id:
                kwargs['category'] = category.tree_path
                url = reverse('static_detail', kwargs=kwargs)
            else:
                url = reverse('home_static_detail', kwargs=kwargs)
        else:
            kwargs.update({
                    'year' : self.publish_from.year,
                    'month' : self.publish_from.month,
                    'day' : self.publish_from.day,
                })
            if category.tree_parent_id:
                kwargs['category'] = category.tree_path
                url = reverse('object_detail', kwargs=kwargs)
            else:
                url = reverse('home_object_detail', kwargs=kwargs)

        if category.site_id != settings.SITE_ID or domain:
            site = get_cached_object(Site, pk=category.site_id)
            return 'http://' + site.domain + url
        return url


def ListingBox(listing, *args, **kwargs):
    " Delegate the boxing to the target's Box class. "
    obj = listing.placement.publishable
    return obj.box_class(obj, *args, **kwargs)

class Listing(models.Model):
    """
    Listing of an object in a category. Each and every object that have it's own detail page must have a Listing object
    that is valid (not expired) and places him in the object's main category. Any object can be listed in any number of
    categories (but only once per category). Even if the object is listed in other categories besides its main category,
    its detail page's url still belongs to the main one.

    see doc/listing.txt for more details on Listings
    """
    box_class = staticmethod(ListingBox)

    placement = models.ForeignKey(Placement)
    category = models.ForeignKey(Category, db_index=True)

    publish_from = models.DateTimeField(_("Start of listing"))
    publish_to = models.DateTimeField(_("End of listing"), null=True, blank=True)

    priority_from = models.DateTimeField(_("Start of prioritized listing"), null=True, blank=True)
    priority_to = models.DateTimeField(_("End of prioritized listing"), null=True, blank=True)
    priority_value = models.IntegerField(_("Priority"), blank=True, null=True)

    commercial = models.BooleanField(_("Commercial"), default=False, help_text=_("Check this if the listing is of a commercial content."))

    objects = ListingManager()

    @property
    def target(self):
        return self.placement.publishable

    def get_absolute_url(self, domain=False):
        return self.placement.get_absolute_url(domain)

    def get_domain_url(self):
        return self.get_absolute_url(domain=True)

    def __unicode__(self):
        try:
            return u'%s listed in %s' % (self.placement.publishable, self.category)
        except:
            return 'Broken listing'

    class Meta:
        app_label = 'core'
        verbose_name = _('Listing')
        verbose_name_plural = _('Listings')
        ordering = ('-publish_from',)

class HitCount(models.Model):
    """
    Count hits for individual objects.
    """
    placement = models.ForeignKey(Placement, primary_key=True)

    last_seen = models.DateTimeField(_('Last seen'), editable=False)
    hits = models.PositiveIntegerField(_('Hits'), default=1)

    objects = HitCountManager()

    def save(self, force_insert=False, force_update=False):
        "update last seen automaticaly"
        self.last_seen = datetime.now()
        super(HitCount, self).save(force_insert, force_update)

    def target(self):
        return self.placement.publishable

    class Meta:
        app_label = 'core'
        verbose_name = 'Hit Count'
        verbose_name_plural = 'Hit Counts'

