from datetime import datetime

from django.db import models
from django.contrib import admin
from django.contrib.contenttypes.models import  ContentType
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _

from ella.core.models import Category, Author, Source, Listing
from ella.core.box import Box
from ella.core.managers import RelatedManager
from ella.photos.models import Photo

class InfoBox(models.Model):
    title = models.CharField(_('Title'), maxlength=255)
    created = models.DateTimeField(_('Created'), default=datetime.now, editable=False)
    updated = models.DateTimeField(_('Updated'), blank=True, null=True)
    content = models.TextField(_('Content'))

    class Meta:
        ordering = ('-created',)
        verbose_name = _('Info box')
        verbose_name_plural = _('Info boxes')


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

    # Main Photo to Article
    photo = models.ForeignKey(Photo, blank=True, null=True, verbose_name=_('Photo'))

    objects = RelatedManager()

    def get_photo(self):
        from ella.core.cache import get_cached_object
        if not hasattr(self, '_photo'):
            try:
                self._photo = get_cached_object(ContentType.objects.get_for_model(Photo), pk=self.photo_id)
            except Photo.DoesNotExist:
                self._photo = None
        return self._photo
    @property
    def main_listing(self):
        from ella.core.cache import get_cached_object
        try:
            return get_cached_object(
                    ContentType.objects.get_for_model(Listing),
                    target_ct=ContentType.objects.get_for_model(self.__class__),
                    target_id=self.id,
                    category=self.category
)
        except Listing.DoesNotExist:
            return None

    def get_absolute_url(self):
        listing = self.main_listing
        if listing:
            return listing.get_absolute_url()

    @property
    def content(self):
        if not hasattr(self, '_content'):
            self._content = self.articlecontents_set.all()[0]
        return self._content

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
        #order_with_respect_to = 'article'

    def __unicode__(self):
        return self.title

TEXTAREACLASS = 'rich_text_area'
class ArticleContentInlineOptions(admin.TabularInline):
    def formfield_for_dbfield(self, db_field, **kwargs):
        from django.newforms import widgets
        if db_field.name == 'content':
            return super(ArticleContentInlineOptions, self).formfield_for_dbfield(
                    db_field,
                    widget=widgets.Textarea(attrs={'class': TEXTAREACLASS,}),
                    **kwargs
)
        return super(ArticleContentInlineOptions, self).formfield_for_dbfield(db_field, **kwargs)

class InfoBoxOptions(admin.ModelAdmin):
    list_display = ('title', 'created',)
    date_hierarchy = 'created'
    list_filter = ('created', 'updated',)
    search_fields = ('title', 'content',)

    def formfield_for_dbfield(self, db_field, **kwargs):
        from django.newforms import widgets
        if db_field.name == 'content':
            return super(InfoBoxOptions, self).formfield_for_dbfield(
                    db_field,
                    widget=widgets.Textarea(attrs={'class': TEXTAREACLASS,}),
                    **kwargs
)
        return super(InfoBoxOptions, self).formfield_for_dbfield(db_field, **kwargs)


admin.site.register(InfoBox, InfoBoxOptions)

class ArticleOptions(admin.ModelAdmin):
    #raw_id_fields = ('authors',)
    list_display = ('title', 'created', 'article_age',)
    date_hierarchy = 'created'
    ordering = ('-created',)
    fields = (
        (_("Article heading"), {'fields': ('title', 'upper_title', 'updated', 'slug')}),
        (_("Article contents"), {'fields': ('perex',)}),
        (_("Metadata"), {'fields': ('category', 'authors', 'source', 'photo')})
)
    raw_id_fields = ('photo',)
    list_filter = ('created', 'category', 'authors',)
    search_fields = ('title', 'perex',)
    inlines = (ArticleContentInlineOptions(ArticleContents, extra=1),)
    prepopulated_fields = {'slug' : ('title',)}

    def formfield_for_dbfield(self, db_field, **kwargs):
        from django.newforms import widgets
        if db_field.name == 'perex':
            return super(ArticleOptions, self).formfield_for_dbfield(
                    db_field,
                    widget=widgets.Textarea(attrs={'class': TEXTAREACLASS,}),
                    **kwargs
)
        return super(ArticleOptions, self).formfield_for_dbfield(db_field, **kwargs)


admin.site.register(Article, ArticleOptions)

