from django.utils.translation import ugettext_lazy as _

from ella.core.newman_admin import ListingInlineAdmin, PublishableAdmin,\
    RelatedInlineAdmin
from ella.articles.models import Article
import ella_newman


class ArticleAdmin(PublishableAdmin):
    fieldsets = (
        (_("Article heading"), {'fields': ('title', )}),
        (_("Updated, slug"), {'fields': ('last_updated', 'slug',), 'classes': ('collapsed',)}),
        (_("Metadata"), {'fields': ('photo', 'category', 'authors', 'source')}),
        (_("Dates"), {'fields': (('publish_from', 'publish_to'), 'static')}),
        (_("Content"), {'fields': ('description', 'content')}),
    )

    inlines = [ListingInlineAdmin, RelatedInlineAdmin]
    rich_text_fields = {'small': ('description',), None: ('content',)}


ella_newman.site.register(Article, ArticleAdmin)
