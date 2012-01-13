from django.utils.translation import ugettext_lazy as _

from ella.core.newman_admin import ListingInlineAdmin, PublishableAdmin,\
    RelatedInlineAdmin
from ella.articles.models import Article, InfoBox
from ella import newman


class InfoBoxAdmin(newman.NewmanModelAdmin):
    list_display = ('title', 'created',)
    date_hierarchy = 'created'
    list_filter = ('created', 'updated',)
    search_fields = ('title', 'content',)
    rich_text_fields = {None: ('content',)}


class ArticleAdmin(PublishableAdmin):
    fieldsets = (
        (_("Article heading"), {'fields': ('title', 'upper_title',)}),
        (_("Updated, slug"), {'fields': ('updated', 'slug',), 'classes': ('collapsed',)}),
        (_("Metadata"), {'fields': ('photo', 'category', 'authors', 'source')}),
        (_("Dates"), {'fields': (('publish_from', 'publish_to'), 'static')}),
        (_("Content"), {'fields': ('description', 'content')}),
    )

    inlines = [ListingInlineAdmin, RelatedInlineAdmin]
    rich_text_fields = {'small': ('description',), None: ('content',)}


newman.site.register(InfoBox, InfoBoxAdmin)
newman.site.register(Article, ArticleAdmin)

