from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from ella.core.admin import PublishableAdmin, ListingInlineAdmin, RelatedInlineAdmin
from ella.articles.models import Article


class ArticleAdmin(PublishableAdmin):
    ordering = ('-publish_from',)
    fieldsets = (
        (_("Article heading"), {'fields': ('title', 'slug')}),
        (_("Article contents"), {'fields': ('description', 'content')}),
        (_("Metadata"), {'fields': ('category', 'authors', 'source', 'photo')}),
        (_("Publication"), {'fields': (('publish_from', 'publish_to'), 'published', 'static')}),
    )
    inlines = [ListingInlineAdmin, RelatedInlineAdmin]


admin.site.register(Article, ArticleAdmin)
