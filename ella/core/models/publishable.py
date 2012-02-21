from datetime import datetime

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.contrib.redirects.models import Redirect

from jsonfield.fields import JSONField

from ella.core.box import Box
from ella.core.conf import core_settings
from ella.core.signals import content_published, content_unpublished
from ella.core.cache import get_cached_object, CachedGenericForeignKey, \
    CachedForeignKey
from ella.core.managers import ListingManager, RelatedManager
from ella.core.models.main import Category, Author, Source
from ella.photos.models import Photo

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
    Base class for all objects that can be published in Ella.
    """
    box_class = staticmethod(PublishableBox)

    content_type = models.ForeignKey(ContentType)
    target = CachedGenericForeignKey('content_type', 'id')

    category = CachedForeignKey(Category, verbose_name=_('Category'))

    # Titles
    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=255)

    # Authors and Sources
    authors = models.ManyToManyField(Author, verbose_name=_('Authors'))
    source = models.ForeignKey(Source, blank=True, null=True,
        verbose_name=_('Source'))

    # Main Photo
    photo = CachedForeignKey(Photo, blank=True, null=True, on_delete=models.SET_NULL,
        verbose_name=_('Photo'))

    # Description
    description = models.TextField(_('Description'), blank=True)

    # Publish data
    published = models.BooleanField(_('Published'))
    publish_from = models.DateTimeField(_('Publish from'),
        default=core_settings.PUBLISH_FROM_WHEN_EMPTY, db_index=True)
    publish_to = models.DateTimeField(_("End of visibility"), null=True, blank=True)
    static = models.BooleanField(_('static'), default=False)

    # generic JSON field to store app cpecific data
    app_data = JSONField(default='{}', blank=True, editable=False)

    # has the content_published signal been sent for this instance?
    announced = models.BooleanField(help_text='Publish signal sent', default=False, editable=False)

    class Meta:
        app_label = 'core'
        verbose_name = _('Publishable object')
        verbose_name_plural = _('Publishable objects')

    def __unicode__(self):
        return self.title

    def get_absolute_url(self, domain=False):
        " Get object's URL. "
        category = self.category

        kwargs = {
            'content_type' : slugify(self.content_type.model_class()._meta.verbose_name_plural),
            'slug' : self.slug,
        }

        if self.static:
            kwargs['id'] = self.pk
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


    def get_domain_url(self):
        return self.get_absolute_url(domain=True)

    def get_domain_url_admin_tag(self):
        if self.get_domain_url() is not None:
            return mark_safe(u'<a href="%s">url</a>' % (self.get_domain_url()))
        else:
            return self.get_domain_url()
    get_domain_url_admin_tag.short_description = _('URL')
    get_domain_url_admin_tag.allow_tags = True

    def save(self, **kwargs):
        self.content_type = ContentType.objects.get_for_model(self)
        send_signal = None
        if self.pk:
            old_self = Publishable.objects.get(pk=self.pk)

            old_path = old_self.get_absolute_url()
            new_path = self.get_absolute_url()

            # detect change in URL
            if old_path != new_path and new_path:
                # and create a redirect
                redirect = Redirect.objects.get_or_create(old_path=old_path,
                    site=self.category.site)[0]
                redirect.new_path = new_path
                redirect.save(force_update=True)
                # also update all potentially already existing redirects
                Redirect.objects.filter(new_path=old_path).exclude(
                    pk=redirect.pk).update(new_path=new_path)

            # detect change in publication status
            if old_self.is_published() != self.is_published():
                if self.is_published():
                    send_signal = content_published
                    self.announced = True
                else:
                    send_signal = content_unpublished
                    self.announced = False
        # published, send the proper signal
        elif self.is_published():
            send_signal = content_published
            self.announced = True

        super(Publishable, self).save(**kwargs)

        if send_signal:
            send_signal.send(sender=self.__class__, publishable=self)

    def delete(self):
        url = self.get_absolute_url()
        Redirect.objects.filter(new_path=url).delete()
        return super(Publishable, self).delete()

    def is_published(self):
        "Return True if the Publishable is currently active."
        now = datetime.now()
        return self.published and now > self.publish_from and \
            (self.publish_to is None or now < self.publish_to)


def ListingBox(listing, *args, **kwargs):
    " Delegate the boxing to the target's Box class. "
    obj = listing.publishable
    return obj.box_class(obj, *args, **kwargs)


class Listing(models.Model):
    """
    Listing of an ``Publishable`` in a ``Category``. Each and every object that have it's 
    own detail page must have a ``Listing`` object that is valid (not expired) and
    places it in the object's main category. Any object can be listed in any
    number of categories (but only once per category). Even if the object is
    listed in other categories besides its main category, its detail page's url
    still belongs to the main one.
    """
    box_class = staticmethod(ListingBox)

    publishable = models.ForeignKey(Publishable, verbose_name=_('Publishable'))
    category = models.ForeignKey(Category, verbose_name=_('Category'), db_index=True)

    publish_from = models.DateTimeField(_("Start of listing"), db_index=True)
    publish_to = models.DateTimeField(_("End of listing"), null=True, blank=True)

    commercial = models.BooleanField(_("Commercial"), default=False,
        help_text=_("Check this if the listing is of a commercial content."))

    objects = ListingManager()

    class Meta:
        app_label = 'core'
        verbose_name = _('Listing')
        verbose_name_plural = _('Listings')

    def __unicode__(self):
        try:
            return _(u'%s listed in %s') % (self.publishable, self.category)
        except:
            return _('Broken listing')

    def get_absolute_url(self, domain=False):
        return self.publishable.get_absolute_url(domain)

    def get_domain_url(self):
        return self.get_absolute_url(domain=True)


class Related(models.Model):
    """
    Related objects - model for recording related ``Publishable`` objects.
    An example would be two articles sharing a similar topic. When something
    like this happens, a ``Related`` instance connecting the objects should
    be created.
    """
    publishable = models.ForeignKey(Publishable, verbose_name=_('Publishable'))

    related_ct = models.ForeignKey(ContentType, verbose_name=_('Content type'))
    related_id = models.IntegerField(_('Object ID'))
    related = CachedGenericForeignKey('related_ct', 'related_id')

    objects = RelatedManager()

    class Meta:
        app_label = 'core'
        verbose_name = _('Related')
        verbose_name_plural = _('Related')

    def __unicode__(self):
        return _(u'%s relates to %s') % (self.publishable, self.related)


