from django.db import models, IntegrityError
from django.utils.translation import ugettext_lazy as _

from ella.core.models import Publishable, Category
from ella.photos.models import Photo
from ella.exports.managers import ExportManager

POSITION_IS_NOT_OVERLOADED = 0

class UnexportableException(Exception):
    pass

class Export(models.Model):
    " Export group. "
    category = models.ForeignKey(Category, verbose_name=_('Category'))
    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=255)
    max_visible_items = models.IntegerField(_('Maximum Visible Fields'))
    objects = ExportManager()

    def __unicode__(self):
        return u'%s: %s (%s)' % (unicode(self._meta.verbose_name), self.title, self.category)

    class Meta:
        unique_together = ( ('title',), ('slug',) )
        verbose_name = _('Export')
        verbose_name_plural = _('Exports')


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

    def save(self, force_insert=False, force_update=False):
        #if not self.title and not self.photo and not self.description:
        #    raise IntegrityError
        super(ExportMeta, self).save(force_insert, force_update)

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
    visible_to = models.DateTimeField(null=True)
    position = models.IntegerField(blank=True, default=POSITION_IS_NOT_OVERLOADED)
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
