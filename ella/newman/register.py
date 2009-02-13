"""
This module is intended as TEMPORARY. Contains registrations for testing purposes only, without affecting EllaAdmin.
Useful for NewmanModelAdmin registrations and other stuff.
"""

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from ella.tagging.admin import TaggingInlineOptions

from ella.core.admin import PlacementInlineOptions
from ella.articles.models import ArticleContents, Article, InfoBox
from ella.ellaadmin.options import EllaAdminOptionsMixin, EllaModelAdmin

from ella.newman import NewmanModelAdmin, site
from django.utils.safestring import mark_safe

class ArticleContentInlineOptions(EllaAdminOptionsMixin, admin.TabularInline):
    model = ArticleContents
    extra = 1
    rich_text_fields = {None: ('content',)}

class InfoBoxOptions(NewmanModelAdmin):
    list_display = ('title', 'created',)
    date_hierarchy = 'created'
    list_filter = ('created', 'updated',)
    search_fields = ('title', 'content',)
    rich_text_fields = {None: ('content',)}

class ArticleOptions(NewmanModelAdmin):
    list_display = ('title', 'category', 'photo_thumbnail', 'created', 'hitcounts', 'obj_url')
    list_display_ext = ('article_age', 'get_hits', 'pk', 'full_url',)
#    date_hierarchy = 'created'
    ordering = ('-created',)
    fieldsets = (
        (_("Article heading"), {'fields': ('title', 'upper_title', 'updated', 'slug')}),
        (_("Article contents"), {'fields': ('perex',)}),
        (_("Metadata"), {'fields': ('category', 'authors', 'source', 'photo')}),
)
    raw_id_fields = ('photo',)
    list_filter = ('category__site', 'created', 'category', 'authors',)
    search_fields = ('title', 'upper_title', 'perex', 'slug', 'authors__name', 'authors__slug',) # FIXME: 'tags__tag__name',)
    inlines = [ ArticleContentInlineOptions, PlacementInlineOptions ]
    if 'ella.tagging' in settings.INSTALLED_APPS:
        inlines.append(TaggingInlineOptions)
    prepopulated_fields = {'slug' : ('title',)}
    rich_text_fields = {None: ('perex',)}
    list_per_page = 20

    def obj_url(self, obj):
        if obj.get_absolute_url():
            return mark_safe('<a href="%s">url</a>' % obj.get_absolute_url())
        return _('No URL')
    obj_url.allow_tags = True
    obj_url.short_description = _('Full URL')

    def hitcounts(self, obj):
        return mark_safe('<a class="icn na" href="">?</a>')
    hitcounts.allow_tags = True
    hitcounts.short_description = _('Hits')




site.register(InfoBox, InfoBoxOptions)
site.register(Article, ArticleOptions)

