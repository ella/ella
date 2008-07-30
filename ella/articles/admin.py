from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from ella.tagging.admin import TaggingInlineOptions

from ella.core.admin import PlacementInlineOptions
from ella.articles.models import ArticleContents, Article, InfoBox


class ArticleContentInlineOptions(admin.TabularInline):
    model = ArticleContents
    extra = 1
    rich_text_fields = {None: ('content',)}

class InfoBoxOptions(admin.ModelAdmin):
    list_display = ('title', 'created',)
    date_hierarchy = 'created'
    list_filter = ('created', 'updated',)
    search_fields = ('title', 'content',)
    rich_text_fields = {None: ('content',)}

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
    search_fields = ('title', 'upper_title', 'perex', 'slug', 'authors__name', 'authors__slug',)
    inlines = (ArticleContentInlineOptions, PlacementInlineOptions, TaggingInlineOptions,)
    prepopulated_fields = {'slug' : ('title',)}
    rich_text_fields = {None: ('perex',)}

    # TODO: generic suggester
    # suggest_fields = {'category': ('title','slug','tree_path',)}

    def formfield_for_dbfield(self, db_field, **kwargs):
        from ella.ellaadmin import fields
        if db_field.name == 'category':
            return fields.CategorySuggestField(db_field, **kwargs)
        return super(ArticleOptions, self).formfield_for_dbfield(db_field, **kwargs)


admin.site.register(InfoBox, InfoBoxOptions)
admin.site.register(Article, ArticleOptions)

