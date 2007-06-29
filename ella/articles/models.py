from datetime import datetime

from django.db import models
from django.contrib import admin

from ella.core.models import *


class Article(models.Model):
    # Titles
    title = models.CharField(maxlength=255)
    upper_title = models.CharField(maxlength=255, blank=True)
    slug = models.SlugField()
    # Contents
    perex = models.TextField()
    content = models.TextField()
#    tags = models.ForeignKey()
#    related = models.ForeignKey()
    # Publication and priorities
    published = models.DateTimeField(default=datetime.now, verbose_name=_("Publication Date"))
    updated = models.DateTimeField(blank=True)
    # Authors and Sources
    author = models.ManyToManyField(Author)
    source = models.ForeignKey(Source, blank=True, null=True)
#    status = models
    # Meta
#    added_by = models.ForeignKey()
#    modified_by = models.ForeignKey()

    def __str__(self):
        return self.title

    def article_age(self):
        return timesince(self.published)
        #return (datetime.now() - self.published).days
    article_age.short_description = _("Article Age")

def parse_nodelist(nodelist):
    for node in nodelist:
        yield node
        for subnodelist in [ getattr(node, key) for key in dir(node) if key.startswith('nodelist') ]:
            for subnode in parse_nodelist(subnodelist):
                yield subnode


class ArticleContents(models.Model):
    article = models.ForeignKey(Article)
    title = models.CharField(maxlength=200)
    content = models.TextField()

    def save(self):
        from django import template
        # parse content, discover dependencies
        t = template.Template('{% load articles %}' + self.content)
        for node in parse_nodelist(t.nodelist):
            if isinstance(node, BoxTag):
                report_dep()

        super(ArticleContents, self).save()
    def __str__(self):
        return self.title

class ArticleOptions(admin.ModelAdmin):
    list_display = ('title', 'published', 'article_age')
    ordering = ('-published',)
    fields = (
        (_("Article Heading"), {'fields': ('title', 'upper_title', 'published', 'updated', 'slug')}),
        (_("Article Contents"), {'fields': ('perex', 'content')}),
        (_("Metadata"), {'fields': ('author', 'source')})
)
    list_filter = ('published',)
    search_fields = ('title', 'perex')
    inlines = [admin.TabularInline(ArticleContents, extra=1)]
    prepopulated_fields = {'slug' : ('title',)}

admin.site.register(Article, ArticleOptions)

