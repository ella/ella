from datetime import datetime, timedelta

from django.db import models, transaction
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from django.template import loader

from ella.core.box import Box
from ella.core.managers import ListingManager, HitCountManager, DependencyManager
from ella.core.cache import get_cached_object, cache_this


class Author(models.Model):
    """
    Author of articles and other publishable content objects.
    All fields except slug are optional.
    """
    user = models.ForeignKey(User, blank=True, null=True)
    name = models.CharField(_('Name'), max_length=200, blank=True)
    slug = models.CharField(_('Slug'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    text = models.TextField(_('Text'), blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering=('name', 'slug',)
        verbose_name = _('Author')
        verbose_name_plural = _('Authors')

class Source(models.Model):
    """
    List of sources for Photos, Articles and other content models.
    May contain description and/or url.
    """
    name = models.CharField(_('Name'), max_length=200)
    url = models.URLField(_('URL'), blank=True)
    description = models.TextField(_('Description'), blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Source')
        verbose_name_plural = _('Sources')
        ordering = ('name',)

class CategoryBox(Box):
    """
    Special Box class for category that adds 'photo_slug' parameter
    to the box's context (if supplied).
    """

    def get_context(self):
        cont = super(CategoryBox, self).get_context()
        if 'photo_slug' in self.params:
            cont['photo_slug'] = self.params['photo_slug']
        return cont

def get_category_key(func, category):
    "Get key for caching category's __unicode__ method."
    return 'ella.core.models.Category:%d' % category.id

class Category(models.Model):
    """
    Basic building block of ella-based sites. All the published content is divided into categories -
    every Publishable object
        has a ForeignKey to it's primary Category
        can be published in other categories (aka "secondary" categories) via Listing

    Every site has exactly one root category (without a parent) that serve's as the sites's homepage.

    see doc/listings.txt for more details.
    """
    title = models.CharField(_("Category Title"), max_length=200)
    slug = models.CharField(_("Slug"), max_length=200)
    tree_parent = models.ForeignKey('self', null=True, blank=True, verbose_name=_("Parent Category"))
    tree_path = models.CharField(verbose_name=_("Path from root category"), max_length=255, editable=False)
    description = models.TextField(_("Category Description"), blank=True)
    site = models.ForeignKey(Site)

    @transaction.commit_on_success
    def save(self):
        "Override save() to construct tree_path based on the category's parent."
        old_tree_path = self.tree_path
        if self.tree_parent:
            if self.tree_parent.tree_path:
                self.tree_path = '%s/%s' % (self.tree_parent.tree_path, self.slug)
            else:
                self.tree_path = self.slug
        else:
            self.tree_path = ''
        super(Category, self).save()
        if old_tree_path != self.tree_path:
            # the tree_path has changed, update children
            children = Category.objects.filter(tree_path__startswith=old_tree_path+'/').order_by('tree_path')
            for child in children:
                child.save()

    def get_tree_parent(self):
        "Cached method."
        if self.tree_parent_id:
            return get_cached_object(Category, pk=self.tree_parent_id)
        return None

    @property
    def path(self):
        "Used in template paths."
        if self.tree_parent_id:
            return self.tree_path
        else:
            return self.slug

    def Box(self, box_type, nodelist):
        "Return custom Box subclass."
        return CategoryBox(self, box_type, nodelist)

    def get_absolute_url(self):
        if not self.tree_parent_id:
            url = reverse('root_homepage')
        else:
            url = reverse(
                    'category_detail',
                    kwargs={
                        'category' : self.tree_path,
}
)
        if self.site_id != settings.SITE_ID:
            # prepend the domain if it doesn't match current Site
            site = get_cached_object(Site, pk=self.site_id)
            return 'http://' + site.domain + url
        return url

    def draw_title(self):
        return mark_safe(('&nbsp;&nbsp;' * self.tree_path.count('/')) + self.title)
    draw_title.allow_tags = True

    class Meta:
        ordering = ('site', 'title',)
        unique_together = (('site', 'tree_path'),)
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    @cache_this(get_category_key)
    def __unicode__(self):
        return '%s/%s' % (self.site.name, self.tree_path)

class Listing(models.Model):
    """
    Listing of an object in a category. Each and every odject that have it's own detail page must have a Listing object
    that is valid (nod expired) and places him in the object's main category. Any object can be listed in any number of
    categories (but only once per category). Even if the object is listed in other categories besides its main category,
    its detail page's url still belongs to the main one.

    see doc/listing.txt for more details on Listings
    """

    # listing's target - a Publishable object
    target_ct = models.ForeignKey(ContentType)
    target_id = models.IntegerField()

    @property
    def target(self):
        "Return target object via cache"
        if not hasattr(self, '_target'):
            target_ct = get_cached_object(ContentType, pk=self.target_ct_id)
            self._target = get_cached_object(target_ct, pk=self.target_id)
        return self._target

    category = models.ForeignKey(Category, db_index=True)

    publish_from = models.DateTimeField(_("Start of listing"))
    priority_from = models.DateTimeField(_("Start of prioritized listing"), null=True, blank=True)
    priority_to = models.DateTimeField(_("End of prioritized listing"), null=True, blank=True)
    priority_value = models.IntegerField(_("Priority"), blank=True, null=True)
    remove = models.BooleanField(_("Remove"), help_text=_("Remove object from listing after the priority wears off?"), default=False)

    commercial = models.BooleanField(_("Commercial"), default=False, help_text=_("Check this if the listing is of a commercial content."))

    hidden = models.BooleanField(_("Hidden"), default=False, help_text=_("Create the object's URL, but do not list it in listings?"))

    objects = ListingManager()

    def Box(self, box_type, nodelist):
        " Delegate the boxing to the target's Box factory method."
        obj = self.target
        if hasattr(obj, 'Box'):
            return obj.Box(box_type, nodelist)
        return Box(obj, box_type, nodelist)

    def get_absolute_url(self):
        "Get the target's absolute URL - find it's primary Listing and make a reverse() match."
        obj = self.target
        if obj.category_id != self.category_id:
            listing = obj.main_listing
        else:
            listing = self

        category = get_cached_object(Category, pk=obj.category_id)

        if category.tree_parent_id:
            url = reverse(
                    'object_detail',
                    kwargs={
                        'category' : category.tree_path,
                        'year' : listing.publish_from.year,
                        'month' : listing.publish_from.month,
                        'day' : listing.publish_from.day,
                        'content_type' : slugify(obj._meta.verbose_name_plural),
                        'slug' : getattr(obj, 'slug', str(obj._get_pk_val())),
}
)
        else:
            url = reverse(
                    'home_object_detail',
                    kwargs={
                        'year' : listing.publish_from.year,
                        'month' : listing.publish_from.month,
                        'day' : listing.publish_from.day,
                        'content_type' : slugify(obj._meta.verbose_name_plural),
                        'slug' : getattr(obj, 'slug', str(obj._get_pk_val())),
}
)
        if category.site_id != settings.SITE_ID:
            site = get_cached_object(Site, pk=category.site_id)
            return 'http://' + site.domain + url
        return url

    def __unicode__(self):
        try:
            return u'%s listed in %s' % (self.target, self.category)
        except models.ObjectDoesNotExist:
            return u'Broken listing in %s' % self.category

    def is_active(self):
        "Return True if the listing's priority is currently active."
        now = datetime.now()
        return not (self.priority_to and now > self.priority_to and self.remove)

    def is_published(self):
        now = datetime.now()
        return (now > self.publish_from)

    def full_url(self):
        "Full url to be shown in admin."
        return mark_safe('<a href="%s">url</a>' % self.get_absolute_url())
    full_url.allow_tags = True

    def save(self):
        " If Listing is created, we create HitCount object "

        # we should non-cached target
        target_ct = get_cached_object(ContentType, pk=self.target_ct_id)
        target = target_ct.model_class().objects.get(pk=self.target_id)

        if target.category_id == self.category_id:
            if not self.id:
                HitCount.objects.create(target_ct=self.target_ct, target_id=self.target_id, site=self.category.site)
            else:
                hc = HitCount.objects.get(target_ct=self.target_ct, target_id=self.target_id)
                hc.site = self.category.site
                hc.save()
        super(Listing, self).save()

    class Meta:
        verbose_name = _('Listing')
        verbose_name_plural = _('Listings')
        ordering = ('-publish_from',)
        unique_together = (('category', 'target_id', 'target_ct'),)

class HitCount(models.Model):
    """
    Count hits for individual objects.
    """
    target_ct = models.ForeignKey(ContentType)
    target_id = models.IntegerField()

    last_seen = models.DateTimeField(_('Last seen'), editable=False)
    site = models.ForeignKey(Site)

    hits = models.PositiveIntegerField(_('Hits'), default=1)

    objects = HitCountManager()

    def save(self):
        "update last seen automaticaly"
        self.last_seen = datetime.now()
        super(HitCount, self).save()

    @property
    def target(self):
        if not hasattr(self, '_target'):
            target_ct = get_cached_object(ContentType, pk=self.target_ct_id)
            self._target = get_cached_object(target_ct, pk=self.target_id)
        return self._target

    class Meta:
        ordering = ('-hits', '-last_seen',)
        verbose_name = 'Hit Count'
        verbose_name_plural = 'Hit Counts'
        unique_together = ('target_ct', 'target_id')

class Related(models.Model):
    """
    Related objects - model for recording related items. For example related articles.
    """
    target_ct = models.ForeignKey(ContentType, related_name='relation_for_set')
    target_id = models.IntegerField()

    source_ct = models.ForeignKey(ContentType, related_name='related_on_set')
    source_id = models.IntegerField()

    @property
    def source(self):
        if not hasattr(self, '_source'):
            source_ct = get_cached_object(ContentType, pk=self.source_ct_id)
            self._source = get_cached_object(source_ct, pk=self.source_id)
        return self._source

    @property
    def target(self):
        if not hasattr(self, '_target'):
            target_ct = get_cached_object(ContentType, pk=self.target_ct_id)
            self._target = get_cached_object(target_ct, pk=self.target_id)
        return self._target

    def __unicode__(self):
        return u'%s relates to %s' % (self.source, self.target)

    class Meta:
        verbose_name = _('Related')
        verbose_name_plural = _('Related')
        ordering = ('source_ct', 'source_id',)

class Dependency(models.Model):
    """
    Dependent objects - model for recording dependent items.
    For example a photo used in an article is the article's dependencies.
    """
    target_ct = models.ForeignKey(ContentType, related_name='dependency_for_set')
    target_id = models.IntegerField()
    target_key = models.CharField(max_length=100, blank=True)

    source_ct = models.ForeignKey(ContentType, related_name='dependent_on_set')
    source_id = models.IntegerField()
    source_key = models.CharField(max_length=100, blank=True)

    objects = DependencyManager()

    @property
    def source(self):
        if not hasattr(self, '_source'):
            source_ct = get_cached_object(ContentType, pk=self.source_ct_id)
            self._source = get_cached_object(source_ct, pk=self.source_id)
        return self._source

    @property
    def target(self):
        if not hasattr(self, '_target'):
            target_ct = get_cached_object(ContentType, pk=self.target_ct_id)
            self._target = get_cached_object(target_ct, pk=self.target_id)
        return self._target

    def __unicode__(self):
        return u'%s depends on %s' % (self.source, self.target)

    class Meta:
        verbose_name = _('Dependency')
        verbose_name_plural = _('Dependencies')
        ordering = ('source_ct', 'source_id',)
        unique_together = (('target_key', 'source_key',),)


from ella.core import register
del register
