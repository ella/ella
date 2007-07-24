from datetime import datetime

from django.db import models
from django.contrib import admin
from django.contrib.contenttypes.models import  ContentType
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _

from ella.core.models import Category, Author, Source, Listing
from ella.core.box import Box


class Article(models.Model):
    # Titles
    title = models.CharField(_('Title'), maxlength=255)
    upper_title = models.CharField(_('Upper title'), maxlength=255, blank=True)
    slug = models.CharField(_('Slug'), maxlength=255)

    # Contents
    perex = models.TextField(_('Perex'))
    created = models.DateTimeField(_('Created'), default=datetime.now, editable=False)
    updated = models.DateTimeField(_('Updated'), blank=True, null=True)

    # Authors and Sources
    authors = models.ManyToManyField(Author, verbose_name=_('Authors'))
    source = models.ForeignKey(Source, blank=True, null=True, verbose_name=_('Source'))
    category = models.ForeignKey(Category, verbose_name=_('Category'))

    @property
    def main_listing(self):
        from ella.core.cache import get_cached_object
        if not hasattr(self, '_main_listing'):
            self._main_listing = get_cached_object(
                ContentType.objects.get_for_model(Listing),
                target_ct=ContentType.objects.get_for_model(Article),
                target_id=self.id,
                category=self.category
)
        return self._main_listing

    @property
    def content(self):
        if not hasattr(self, '_content'):
            self._content = self.articlecontents_set.all()[0]
        return self._content

    @property
    def contents(self):
        if not hasattr(self, '_contents'):
            self._contents = list(self.articlecontents_set.all())
        return self._contents


    def Box(self, box_type, nodelist):
        return Box(self, box_type, nodelist)

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')
        ordering = ('-created',)

    def __unicode__(self):
        return self.title

    def article_age(self):
        return timesince(self.created)
    article_age.short_description = _('Article Age')

    def get_absolute_url(self):
        return self.main_listing.get_absolute_url()

def parse_nodelist(nodelist):
    for node in nodelist:
        yield node
        for subnodelist in [ getattr(node, key) for key in dir(node) if key.startswith('nodelist') ]:
            for subnode in parse_nodelist(subnodelist):
                yield subnode


class ArticleContents(models.Model):
    article = models.ForeignKey(Article, verbose_name=_('Article'))
    title = models.CharField(_('Title'), maxlength=200, blank=True)
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
        order_with_respect_to = 'article'

    def __unicode__(self):
        return self.title

class ArticleOptions(admin.ModelAdmin):
    #raw_id_fields = ('authors',)
    list_display = ('title', 'created', 'article_age',)
    ordering = ('-created',)
    fields = (
        (_("Article heading"), {'fields': ('title', 'upper_title', 'updated', 'slug')}),
        (_("Article contents"), {'fields': ('perex',)}),
        (_("Metadata"), {'fields': ('category', 'authors', 'source',)})
)
    list_filter = ('created',)
    search_fields = ('title', 'perex',)
    inlines = (admin.TabularInline(ArticleContents, extra=3),)
    prepopulated_fields = {'slug' : ('title',)}

admin.site.register(Article, ArticleOptions)

