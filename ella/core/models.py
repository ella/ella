from datetime import datetime

from django.db import models, transaction
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from django.contrib.redirects.models import Redirect

from ella.ellaadmin.utils import admin_url
from ella.core.box import Box
from ella.core.managers import ListingManager, HitCountManager, PlacementManager,\
    RelatedManager
from ella.core.cache import get_cached_object, cache_this, CachedGenericForeignKey

LISTING_UNIQUE_DEFAULT_SET = 'unique_set_default'

class Author(models.Model):
    """
    Author of articles and other publishable content objects.
    All fields except slug are optional.
    """
    user = models.ForeignKey(User, blank=True, null=True)
    name = models.CharField(_('Name'), max_length=200, blank=True)
    slug = models.SlugField(_('Slug'), max_length=255, unique=True)
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
    slug = models.SlugField(_('Slug'), max_length=255)
    tree_parent = models.ForeignKey('self', null=True, blank=True, verbose_name=_("Parent Category"))
    tree_path = models.CharField(verbose_name=_("Path from root category"), max_length=255, editable=False)
    description = models.TextField(_("Category Description"), blank=True)
    site = models.ForeignKey(Site)

    objects = RelatedManager()

    @transaction.commit_on_success
    def save(self, force_insert=False, force_update=False):
        "Override save() to construct tree_path based on the category's parent."
        old_tree_path = self.tree_path
        if self.tree_parent:
            if self.tree_parent.tree_path:
                self.tree_path = '%s/%s' % (self.tree_parent.tree_path, self.slug)
            else:
                self.tree_path = self.slug
        else:
            self.tree_path = ''
        super(Category, self).save(force_insert, force_update)
        if old_tree_path != self.tree_path:
            # the tree_path has changed, update children
            children = Category.objects.filter(tree_path__startswith=old_tree_path+'/').order_by('tree_path')
            for child in children:
                child.save(force_update=True)

    def get_tree_parent(self):
        "Cached method."
        if self.tree_parent_id:
            return get_cached_object(Category, pk=self.tree_parent_id)
        return None

    @property
    def main_parent(self):
        """
        Cached. Used for highlight main category via ifequal tag.
        """
        def _get_main_parent(category):
            if not category.get_tree_parent():
                return None
            if not category.get_tree_parent().get_tree_parent():
                return category
            else:
                return _get_main_parent(category.get_tree_parent())
        return _get_main_parent(self)

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
        unique_together = (('site', 'tree_path'),)
        # TODO: ordering only for admin (admin now use only first item in list)
        ordering = ('site', 'tree_path',)
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    @cache_this(get_category_key)
    def __unicode__(self):
        return '%s/%s' % (self.site.name, self.tree_path)

class Placement(models.Model):
    # listing's target - a Publishable object
    target_ct = models.ForeignKey(ContentType)
    target_id = models.IntegerField()
    target = CachedGenericForeignKey('target_ct', 'target_id')
    category = models.ForeignKey(Category, db_index=True)
    publish_from = models.DateTimeField(_("Start of visibility")) #, default=datetime.now)
    publish_to = models.DateTimeField(_("End of visibility"), null=True, blank=True)
    slug = models.SlugField(_('Slug'), max_length=255, blank=True)

    static = models.BooleanField(default=False)

    objects = PlacementManager()

    class Meta:
        ordering = ('-publish_from',)
        verbose_name = _('Placement')
        verbose_name_plural = _('Placements')

    def __unicode__(self):
        try:
            return u'%s placed in %s' % (self.target, self.category)
        except:
            return 'Broken placement'

    def target_admin(self):
        return self.target
    target_admin.short_description = _('Target')

    def full_url(self):
        "Full url to be shown in admin."
        return mark_safe('<a href="%s">url</a>' % self.get_absolute_url())
    full_url.allow_tags = True


    def is_active(self):
        "Return True if the listing's priority is currently active."
        now = datetime.now()
        return now > self.publish_from and (self.publish_to is None or now < self.publish_to)

    @transaction.commit_on_success
    def save(self, force_insert=False, force_update=False):
        " If Listing is created, we create HitCount object "

        if not self.slug:
            self.slug = getattr(self.target, 'slug', self.target_id)

        if self.pk:
            old_self = Placement.objects.get(pk=self.pk)

            old_path = old_self.get_absolute_url()
            new_path = self.get_absolute_url()

            if old_path != new_path and new_path:
                redirect, created = Redirect.objects.get_or_create(old_path=old_path, new_path=new_path, defaults={'site_id' : settings.SITE_ID})
                for r in Redirect.objects.filter(new_path=old_path).exclude(pk=redirect.pk):
                    r.new_path = new_path
                    r.save()
        # First, save Placement
        super(Placement, self).save(force_insert, force_update)
        # Then, save HitCount (needs placement_id)
        hc, created = HitCount.objects.get_or_create(placement=self)

    def get_absolute_url(self, domain=False):
        obj = self.target
        category = get_cached_object(Category, pk=self.category_id)

        kwargs = {
            'content_type' : slugify(obj._meta.verbose_name_plural),
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


class Listing(models.Model):
    """
    Listing of an object in a category. Each and every object that have it's own detail page must have a Listing object
    that is valid (nod expired) and places him in the object's main category. Any object can be listed in any number of
    categories (but only once per category). Even if the object is listed in other categories besides its main category,
    its detail page's url still belongs to the main one.

    see doc/listing.txt for more details on Listings
    """

    placement = models.ForeignKey(Placement)
    category = models.ForeignKey(Category, db_index=True)

    publish_from = models.DateTimeField(_("Start of listing")) #, default=datetime.now)
    priority_from = models.DateTimeField(_("Start of prioritized listing"), null=True, blank=True)
    priority_to = models.DateTimeField(_("End of prioritized listing"), null=True, blank=True)
    priority_value = models.IntegerField(_("Priority"), blank=True, null=True)
    remove = models.BooleanField(_("Remove"), help_text=_("Remove object from listing after the priority wears off?"), default=False)

    commercial = models.BooleanField(_("Commercial"), default=False, help_text=_("Check this if the listing is of a commercial content."))

    objects = ListingManager()

    @property
    def target(self):
        return self.placement.target


    def Box(self, box_type, nodelist):
        " Delegate the boxing to the target's Box factory method."
        try:
            obj = self.placement.target
        except:
            return None
        if hasattr(obj, 'Box'):
            return obj.Box(box_type, nodelist)
        return Box(obj, box_type, nodelist)

    def get_absolute_url(self, domain=False):
        return self.placement.get_absolute_url(domain)

    def get_domain_url(self):
        return self.get_absolute_url(domain=True)

    def get_publish_from(self):
        return self.publish_from


    def __unicode__(self):
        try:
            return u'%s listed in %s' % (self.placement.target, self.category)
        except:
            return 'Broken listing'

    def target_admin(self):
        return mark_safe('<a href="%s">%s</a>' % (admin_url(self.target), self.target,))
    target_admin.allow_tags = True
    target_admin.short_description = _('edit target')

    def target_url(self):
        "Full url to be shown in admin."
        return mark_safe('<a href="%s">url</a>' % self.get_absolute_url())
    target_url.allow_tags = True
    target_url.short_description = _('target url')

    def target_ct(self):
        return self.target._meta.verbose_name
    target_ct.short_description = _('target ct')

    def target_hitcounts(self):
        hits = HitCount.objects.get(placement=self.placement)
        return mark_safe('<strong>%d</strong>' % hits.hits)
    target_hitcounts.allow_tags = True
    target_hitcounts.short_description = _('hit counts')

    def placement_admin(self):
        return mark_safe('<a href="%s">%s</a>' % (admin_url(self.placement), '::',))
    placement_admin.allow_tags = True
    placement_admin.short_description = ''

    class Meta:
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
        return self.placement.target

    class Meta:
        verbose_name = 'Hit Count'
        verbose_name_plural = 'Hit Counts'

class Related(models.Model):
    """
    Related objects - model for recording related items. For example related articles.
    """
    target_ct = models.ForeignKey(ContentType, related_name='relation_for_set')
    target_id = models.IntegerField()
    target = CachedGenericForeignKey('target_ct', 'target_id')

    source_ct = models.ForeignKey(ContentType, related_name='related_on_set')
    source_id = models.IntegerField()
    source = CachedGenericForeignKey('source_ct', 'source_id')

    def __unicode__(self):
        return u'%s relates to %s' % (self.source, self.target)

    class Meta:
        verbose_name = _('Related')
        verbose_name_plural = _('Related')
        ordering = ('source_ct', 'source_id',)

