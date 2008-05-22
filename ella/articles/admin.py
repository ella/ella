from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from tagging.models import TaggingInlineOptions

from ella.core.admin import ListingInlineOptions
from ella.ellaadmin import fields
from ella.articles.models import ArticleContents, Article, InfoBox


class ArticleContentInlineOptions(admin.TabularInline):
    model = ArticleContents
    extra = 1
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'content':
            if db_field.blank:
                kwargs['required'] = False
            return fields.RichTextAreaField(**kwargs)
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)


class InfoBoxOptions(admin.ModelAdmin):
    list_display = ('title', 'created',)
    date_hierarchy = 'created'
    list_filter = ('created', 'updated',)
    search_fields = ('title', 'content',)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'content':
            if db_field.blank:
                kwargs['required'] = False
            return fields.RichTextAreaField(**kwargs)
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)


class ArticleOptions(admin.ModelAdmin):
    list_display = ('title', 'category', 'photo_thumbnail', 'created', 'article_age', 'get_hits', 'full_url',)
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
    inlines = (ArticleContentInlineOptions, ListingInlineOptions, TaggingInlineOptions,)
    prepopulated_fields = {'slug' : ('title',)}


    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'perex':
            return fields.RichTextAreaField(**kwargs)
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)

admin.site.register(InfoBox, InfoBoxOptions)
admin.site.register(Article, ArticleOptions)

