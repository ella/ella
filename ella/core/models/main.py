from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User

from ella.core.box import Box
from ella.core.cache import get_cached_object, cache_this, CachedGenericForeignKey


class Author(models.Model):
    """
    Author of articles and other publishable content objects.
    All fields except slug are optional.
    """
    user = models.ForeignKey(User, verbose_name=_('User'), blank=True, null=True)
    name = models.CharField(_('Name'), max_length=200, blank=True)
    slug = models.SlugField(_('Slug'), max_length=255, unique=True)
    description = models.TextField(_('Description'), blank=True)
    text = models.TextField(_('Text'), blank=True)
    email = models.EmailField(_('Email'), blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'core'
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
        app_label = 'core'
        verbose_name = _('Source')
        verbose_name_plural = _('Sources')

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
    if category.id is None:
        return None
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

    def save(self, **kwargs):
        "Override save() to construct tree_path based on the category's parent."
        old_tree_path = self.tree_path
        if self.tree_parent:
            if self.tree_parent.tree_path:
                self.tree_path = '%s/%s' % (self.tree_parent.tree_path, self.slug)
            else:
                self.tree_path = self.slug
        else:
            self.tree_path = ''
        super(Category, self).save(**kwargs)
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
        app_label = 'core'
        unique_together = (('site', 'tree_path'),)
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ('site__name', 'tree_path',)

    @cache_this(get_category_key)
    def __unicode__(self):
        return '%s/%s' % (self.site.name, self.tree_path)

class Dependency(models.Model):
    """
    Object dependency - model for recording dependent items. For example when we use photo in article content.
    """

    target_ct = models.ForeignKey(ContentType, related_name='dependency_for_set')
    target_id = models.IntegerField()
    target = CachedGenericForeignKey('target_ct', 'target_id')

    dependent_ct = models.ForeignKey(ContentType, related_name='depends_on_set')
    dependent_id = models.IntegerField()
    dependent = CachedGenericForeignKey('dependent_ct', 'dependent_id')

    def __unicode__(self):
        return u'%s depends on %s' % (self.dependent, self.target)

    class Meta:
        app_label = 'core'
        verbose_name = _('Dependency')
        verbose_name_plural = _('Dependencies')
        ordering = ('dependent_ct', 'dependent_id',)
