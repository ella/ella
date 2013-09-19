from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _, ugettext
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.contrib.redirects.models import Redirect
from django.core.validators import validate_slug
from django.core.exceptions import ValidationError

from app_data import AppDataField

from ella.core.box import Box
from ella.core.cache import CachedGenericForeignKey, \
    CachedForeignKey, ContentTypeForeignKey, CategoryForeignKey
from ella.core.conf import core_settings
from ella.core.managers import ListingManager, RelatedManager, \
    PublishableManager
from ella.core.models.main import Author, Source
from ella.core.signals import content_published, content_unpublished
from ella.utils.timezone import now, localize


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

    content_type = ContentTypeForeignKey(editable=False)
    target = CachedGenericForeignKey('content_type', 'id')

    category = CategoryForeignKey(verbose_name=_('Category'))

    # Titles
    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=255, validators=[validate_slug])

    # Authors and Sources
    authors = models.ManyToManyField(Author, verbose_name=_('Authors'))
    source = CachedForeignKey(Source, blank=True, null=True,
        verbose_name=_('Source'), on_delete=models.SET_NULL)

    # Main Photo
    photo = CachedForeignKey('photos.Photo', blank=True, null=True, on_delete=models.SET_NULL,
        verbose_name=_('Photo'))

    # Description
    description = models.TextField(_('Description'), blank=True)

    # Publish data
    published = models.BooleanField(_('Published'))
    publish_from = models.DateTimeField(_('Publish from'),
        default=core_settings.PUBLISH_FROM_WHEN_EMPTY, db_index=True)
    publish_to = models.DateTimeField(_("End of visibility"), null=True, blank=True)
    static = models.BooleanField(_('static'), default=False)

    # Last updated
    last_updated = models.DateTimeField(_('Last updated'), blank=True)

    # generic JSON field to store app cpecific data
    app_data = AppDataField(default='{}', editable=False)

    # has the content_published signal been sent for this instance?
    announced = models.BooleanField(help_text='Publish signal sent', default=False, editable=False)

    objects = PublishableManager()

    class Meta:
        app_label = 'core'
        verbose_name = _('Publishable object')
        verbose_name_plural = _('Publishable objects')

    def __unicode__(self):
        return self.title

    def __eq__(self, other):
        return isinstance(other, Publishable) and self.pk == other.pk

    def get_absolute_url(self, domain=False):
        " Get object's URL. "
        category = self.category

        kwargs = {
            'slug': self.slug,
        }

        if self.static:
            kwargs['id'] = self.pk
            if category.tree_parent_id:
                kwargs['category'] = category.tree_path
                url = reverse('static_detail', kwargs=kwargs)
            else:
                url = reverse('home_static_detail', kwargs=kwargs)
        else:
            publish_from = localize(self.publish_from)
            kwargs.update({
                    'year': publish_from.year,
                    'month': publish_from.month,
                    'day': publish_from.day,
                })
            if category.tree_parent_id:
                kwargs['category'] = category.tree_path
                url = reverse('object_detail', kwargs=kwargs)
            else:
                url = reverse('home_object_detail', kwargs=kwargs)

        if category.site_id != settings.SITE_ID or domain:
            return 'http://' + category.site.domain + url
        return url

    def get_domain_url(self):
        return self.get_absolute_url(domain=True)

    def clean(self):
        if self.static or not self.published:
            return

        # fields are missing, validating uniqueness is pointless
        if not self.category_id or not self.publish_from or not self.slug:
            return

        qset = self.__class__.objects.filter(
                category=self.category,
                published=True,
                publish_from__day=self.publish_from.day,
                publish_from__month=self.publish_from.month,
                publish_from__year=self.publish_from.year,
                slug=self.slug
            )

        if self.pk:
            qset = qset.exclude(pk=self.pk)

        if qset:
            raise ValidationError(_('Another %s already published at this URL.') % self._meta.verbose_name)

    def save(self, **kwargs):
        # update the content_type if it isn't already set
        if not self.content_type_id:
            self.content_type = ContentType.objects.get_for_model(self)
        send_signal = None
        old_self = None
        if self.pk:
            try:
                old_self = self.__class__.objects.get(pk=self.pk)
            except Publishable.DoesNotExist:
                pass

        if old_self:
            old_path = old_self.get_absolute_url()
            new_path = self.get_absolute_url()

            # detect change in URL and not a static one
            if old_path != new_path and new_path and not old_self.static:
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

            # @note: We also need to check for `published` flag even if both
            # old and new self `is_published()` method returns false.
            # This method can report false since we might be in time *before*
            # publication should take place but we still need to fire signal
            # that content has been unpublished.
            if old_self.published != self.published and self.published is False:
                send_signal= content_unpublished
                self.announced = False

            # changed publish_from and last_updated was default, change it too
            if old_self.last_updated == old_self.publish_from and self.last_updated == old_self.last_updated:
                self.last_updated = self.publish_from

            #TODO: shift Listing in case publish_(to|from) changes
        # published, send the proper signal
        elif self.is_published():
            send_signal = content_published
            self.announced = True

        if not self.last_updated:
            self.last_updated = self.publish_from

        super(Publishable, self).save(**kwargs)

        if send_signal:
            send_signal.send(sender=self.__class__, publishable=self)

    def delete(self):
        url = self.get_absolute_url()
        Redirect.objects.filter(new_path=url).delete()
        if self.announced:
            content_unpublished.send(sender=self.__class__, publishable=self)
        return super(Publishable, self).delete()

    def is_published(self):
        "Return True if the Publishable is currently active."
        cur_time = now()
        return self.published and cur_time > self.publish_from and \
            (self.publish_to is None or cur_time < self.publish_to)


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

    publishable = CachedForeignKey(Publishable, verbose_name=_('Publishable'))
    category = CategoryForeignKey(verbose_name=_('Category'), db_index=True)

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
            return ugettext(u'%(pub)s listed in %(cat)s') % {'pub': self.publishable, 'cat': self.category}
        except:
            return ugettext('Broken listing')

    def clean(self):
        if not self.publishable:
            return

        if self.publish_from and self.publish_from < self.publishable.publish_from:
            raise ValidationError(_('A publishable cannot be listed before it\'s published.'))

        if self.publishable.publish_to:
            if not self.publish_to or self.publish_to > self.publishable.publish_to:
                raise ValidationError(_('A publishable cannot be listed longer than it\'s published.'))

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

    related_ct = ContentTypeForeignKey(verbose_name=_('Content type'))
    related_id = models.IntegerField(_('Object ID'))
    related = CachedGenericForeignKey('related_ct', 'related_id')

    objects = RelatedManager()

    class Meta:
        app_label = 'core'
        verbose_name = _('Related')
        verbose_name_plural = _('Related')

    def __unicode__(self):
        return _(u'%(pub)s relates to %(rel)s') % {'pub': self.publishable, 'rel': self.related}


