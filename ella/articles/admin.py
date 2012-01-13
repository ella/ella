from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from ella.core.admin import PublishableAdmin, ListingInlineAdmin
from ella.articles.models import Article, InfoBox


class InfoBoxAdmin(admin.ModelAdmin):
    list_display = ('title', 'created',)
    date_hierarchy = 'created'
    list_filter = ('created', 'updated',)
    search_fields = ('title', 'content',)
    rich_text_fields = {None: ('content',)}


class ArticleAdmin(PublishableAdmin):
    ordering = ('-created',)
    fieldsets = (
        (_("Article heading"), {'fields': ('title', 'upper_title', 'updated', 'slug')}),
        (_("Article contents"), {'fields': ('description', 'content')}),
        (_("Metadata"), {'fields': ('category', 'authors', 'source', 'photo')}),
        (_("Publication"), {'fields': (('publish_from', 'publish_to'), 'static')}),
    )
    inlines = [ListingInlineAdmin]


admin.site.register(InfoBox, InfoBoxAdmin)
admin.site.register(Article, ArticleAdmin)
