from datetime import datetime

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.timesince import timesince
from django.utils.translation import ugettext, ugettext_lazy as _

from ella.core.models import Category, Author, Source, Listing
from ella.core.box import Box
from ella.core.managers import RelatedManager
from ella.photos.models import Photo

class InfoBox(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    created = models.DateTimeField(_('Created'), default=datetime.now, editable=False)
    updated = models.DateTimeField(_('Updated'), blank=True, null=True)
    content = models.TextField(_('Content'))

    class Meta:
        ordering = ('-created',)
        verbose_name = _('Info box')
        verbose_name_plural = _('Info boxes')

class Article(models.Model):
    # Titles
    title = models.CharField(_('Title'), max_length=255)
    upper_title = models.CharField(_('Upper title'), max_length=255, blank=True)
    slug = models.CharField(_('Slug'), db_index=True, max_length=255)

    # Contents
    perex = models.TextField(_('Perex'))
    created = models.DateTimeField(_('Created'), default=datetime.now, editable=False)
    updated = models.DateTimeField(_('Updated'), blank=True, null=True)

    # Authors and Sources
    authors = models.ManyToManyField(Author, verbose_name=_('Authors'))
    source = models.ForeignKey(Source, blank=True, null=True, verbose_name=_('Source'))
    category = models.ForeignKey(Category, verbose_name=_('Category'))

    # Main Photo to Article
    photo = models.ForeignKey(Photo, blank=True, null=True, verbose_name=_('Photo'))

    objects = RelatedManager()

    def get_photo(self):
        from ella.core.cache import get_cached_object
        if not hasattr(self, '_photo'):
            try:
                self._photo = get_cached_object(Photo, pk=self.photo_id)
            except Photo.DoesNotExist:
                self._photo = None
        return self._photo
    @property
    def main_listing(self):
        from ella.core.cache import get_cached_object
        try:
            return get_cached_object(
                    Listing,
                    target_ct=ContentType.objects.get_for_model(self.__class__),
                    target_id=self.id,
                    category=self.category_id
)
        except Listing.DoesNotExist:
            return None

    def get_absolute_url(self):
        listing = self.main_listing
        if listing:
            return listing.get_absolute_url()

    def full_url(self):
        from django.utils.safestring import mark_safe
        absolute_url = self.get_absolute_url()
        if absolute_url:
            return mark_safe('<a href="%s">url</a>' % absolute_url)
        return 'no url'
    full_url.allow_tags = True


    @property
    def content(self):
        from ella.core.cache import get_cached_list
        if not hasattr(self, '_content'):
            self._contents = get_cached_list(ArticleContents, article=self)
        if self._contents:
            return self._contents[0]
        else:
            return None

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')
        ordering = ('-created',)

    def __unicode__(self):
        return self.title

    def article_age(self):
        return timesince(self.created)
    article_age.short_description = _('Article Age')

    def photo_thumbnail(self):
        from django.utils.safestring import mark_safe
        photo = self.get_photo()
        if photo:
            return mark_safe(photo.thumb())
        else:
            return mark_safe('<div class="errors"><ul class="errorlist"><li>%s</li></ul></div>' % ugettext('No main photo!'))
    photo_thumbnail.allow_tags = True


def parse_nodelist(nodelist):
    for node in nodelist:
        yield node
        for subnodelist in [ getattr(node, key) for key in dir(node) if key.startswith('nodelist') ]:
            for subnode in parse_nodelist(subnodelist):
                yield subnode


class ArticleContents(models.Model):
    article = models.ForeignKey(Article, verbose_name=_('Article'))
    title = models.CharField(_('Title'), max_length=200, blank=True)
    content = models.TextField(_('Content'))

    # @transaction.comit_on_success
    def save(self):
        from django import template
        from ella.core.templatetags import core
        # parse content, discover dependencies
        #t = template.Template('{% load core %}' + self.content)
        #for node in parse_nodelist(t.nodelist):
        #    if isinstance(node, core.BoxTag):
        #        report_dep()
        super(ArticleContents, self).save()

    class Meta:
        verbose_name = _('Article content')
        verbose_name_plural = _('Article contents')
        #order_with_respect_to = 'article'

    def __unicode__(self):
        return self.title


# initialization
from ella.articles import register
del register

