from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.template.defaultfilters import slugify

from ella.core.cache import CachedForeignKey
from ella.core.models import Category
from ella.core.cache import get_cached_list, get_cached_object, cache_this
from ella.menu.managers import MenuItemManager
from ella.db.models import Publishable


class Menu(models.Model):
    slug = models.SlugField(_('Slug'), max_length=255)
    site = models.ForeignKey(Site)
    category = models.ForeignKey(Category)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return unicode('%s for category %s on %s' % (self.slug, self.category, self.site))

    @property
    def menu_slug(self):
        return unicode(self.slug)

    class Meta:
        ordering = ('slug', 'category', 'site')

class MenuItem(models.Model):
    parent = CachedForeignKey('self', blank=True, null=True, verbose_name=_('parent'))
    target_id = models.PositiveIntegerField(null=True, blank=True)
    target_ct = models.ForeignKey(ContentType, null=True, blank=True)
    target = generic.GenericForeignKey(ct_field="target_ct", fk_field="target_id")
    url = models.URLField(blank=True)
    label = models.CharField(max_length=100, blank=True)
    menu = models.ForeignKey(Menu)
    order = models.IntegerField(default=1)
    description = models.TextField(blank=True)

    objects = MenuItemManager()

    def __unicode__(self):
        out = '<UNKNOWN>'
        #import pdb;pdb.set_trace()
        if self.target and not self.label:
            if hasattr(self.target, 'title'):
                out = self.target.title
            elif hasattr(self.target, 'slug'):
                out = self.target.slug
        elif self.label:
            out = self.label
        return unicode(out)

    @property
    def subitems(self):
        #return get_cached_list(MenuItem, parent=self.pk)
        return MenuItem.objects.filter(parent=self.pk).order_by('order')

    def get_url(self):
        """ url magic for fancier notation esp. in templates """
        if self.url:
            return self.url
        elif isinstance(self.target, (Publishable, Category)):
            return self.target.get_absolute_url()

    def get_slug(self):
        if isinstance(self.target, (Publishable, Category)):
            return self.target.slug
        elif self.label:
            return slugify(self.label)

    class Meta:
        verbose_name = _('Menu item')
        verbose_name_plural = _('Menu items')


# initialization
from ella.menu import register
del register
