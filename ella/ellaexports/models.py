import hashlib

from django.db import models, IntegrityError
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

from ella.core.models import Publishable, Category
from ella.core.cache import get_cached_object
from ella.photos.models import Photo, Format
from ella.ellaexports.managers import ExportManager
from ella.ellaexports.conf import ellaexports_settings

class UnexportableException(Exception):
    pass

class Export(models.Model):
    " Export group. "
    category = models.ForeignKey(Category, verbose_name=_('Category'))
    use_objects_in_category = models.BooleanField(_('Use objects listed in category'))
    title = models.CharField(_('Title'), max_length=255)
    link = models.URLField(_('Link'), max_length=255, blank=True)
    description = models.TextField(_('Description'), blank=True)
    slug = models.SlugField(_('Slug'), max_length=255)
    max_visible_items = models.IntegerField(_('Maximum Visible Items'))
    photo_format = models.ForeignKey(Format, verbose_name=_('Photo format'))

    objects = ExportManager()

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.category)

    @property
    def url(self):
        if self.link:
            return self.link
        if not self.slug:
            return ''
        url = reverse('ella_exports_by_slug', args=(self.slug,))
        # prepend the domain if it doesn't match current Site
        site = get_cached_object(Site, pk=self.category.site_id)
        return 'http://' + site.domain + url

    @property
    def get_atom_id(self):
        token = '%s.%s.%s' % (
            self.slug,
            self.max_visible_items,
            self.photo_format,
        )
        hash = hashlib.sha1(token)
        return 'tag:%s' % hash.hexdigest()

    @property
    def items(self):
        return Export.objects.get_items_for_slug(self.slug)

    class Meta:
        unique_together = ( ('title',), ('slug',) )
        verbose_name = _('Export')
        verbose_name_plural = _('Exports')


class AggregatedExport(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    link = models.URLField(_('Link'), max_length=255, blank=True)
    description = models.TextField(_('Description'), blank=True)
    slug = models.SlugField(_('Slug'), max_length=255)
    exports = models.ManyToManyField(Export, verbose_name=_('Exports'))

    def __unicode__(self):
        return self.title

    @property
    def parts(self):
        return self.exports.all()

    class Meta:
        unique_together = ( ('title',), ('slug',) )
        verbose_name = _('Aggregated export')
        verbose_name_plural = _('Aggregated  exports')


class ExportMeta(models.Model):
    """
    Redefine title, photo etc. for exported object
    """

    publishable = models.ForeignKey(Publishable, verbose_name=_('Publishable object'))
    title = models.CharField(_('Title'), max_length=64, blank=True)
    photo = models.ForeignKey(Photo, verbose_name=_('Photo'), blank=True, null=True)
    description = models.TextField(_('Description'), blank=True)

    def __unicode__(self):
        return u"%s: %s" % (_('Redefined export'), self.publishable)

    def get_overloaded_attribute(self, attribute):
        if attribute in self.__dict__ and self.__dict__[attribute]:
            return self.__dict__[attribute]
        if attribute in self.publishable.__dict__:
            return self.publishable.__dict__[attribute]
        return None

    def get_title(self):
        return self.get_overloaded_attribute('title')

    def get_photo(self):
        return self.get_overloaded_attribute('photo')

    def get_description(self):
        return self.get_overloaded_attribute('description')

    class Meta:
        verbose_name = _('Export meta')
        verbose_name_plural = _('Export metas')


class ExportPosition(models.Model):
    " Defines visibility of ExportMeta object. "
    visible_from = models.DateTimeField()
    visible_to = models.DateTimeField(blank=True, null=True)
    position = models.IntegerField(blank=True, default=ellaexports_settings.POSITION_IS_NOT_OVERLOADED)
    object = models.ForeignKey(ExportMeta, verbose_name=_('Export meta'))
    export = models.ForeignKey(Export, verbose_name=_('Export'))

    def save(self, **kwargs):
        if self.export:
            if self.export.max_visible_items < self.position:
                raise IntegrityError
        super(ExportPosition, self).save(**kwargs)

    def __unicode__(self):
        return u'#%d %s - %s for %s' % (self.position, self.visible_from, self.visible_to, self.object)

    class Meta:
        verbose_name = _('Export Position')
        verbose_name_plural = _('Export Positions')

# EOF
