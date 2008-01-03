from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from ella.articles.models import ArticleContents, Article, InfoBox
from ella.ellaadmin import widgets

class ArticleContentInlineOptions(admin.TabularInline):
    model = ArticleContents
    extra = 1
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'content':
            kwargs['widget'] = widgets.RichTextAreaWidget
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)

class InfoBoxOptions(admin.ModelAdmin):
    list_display = ('title', 'created',)
    date_hierarchy = 'created'
    list_filter = ('created', 'updated',)
    search_fields = ('title', 'content',)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'content':
            kwargs['widget'] = widgets.RichTextAreaWidget
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)

from ella.core.admin.models import ListingInlineOptions, HitCountInlineOptions
from tagging.models import TaggingInlineOptions
class ArticleOptions(admin.ModelAdmin):
    #raw_id_fields = ('authors',)
    list_display = ('title', 'category', 'photo_thumbnail', 'created', 'article_age', 'full_url',)
    date_hierarchy = 'created'
    ordering = ('-created',)
    fieldsets = (
        (_("Article heading"), {'fields': ('title', 'upper_title', 'updated', 'slug')}),
        (_("Article contents"), {'fields': ('perex',)}),
        (_("Metadata"), {'fields': ('category', 'authors', 'source', 'photo')}),
)
    raw_id_fields = ('photo',)
    list_filter = ('category__site', 'created', 'category', 'authors',)
    search_fields = ('title', 'upper_title', 'perex', 'slug',)
#    inlines = (ArticleContentInlineOptions, ListingInlineOptions, TaggingInlineOptions, HitCountInlineOptions)
    inlines = (ArticleContentInlineOptions, ListingInlineOptions, TaggingInlineOptions,)
    prepopulated_fields = {'slug' : ('title',)}

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'perex':
            kwargs['widget'] = widgets.RichTextAreaWidget
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)

admin.site.register(InfoBox, InfoBoxOptions)
admin.site.register(Article, ArticleOptions)

