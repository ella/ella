from django.utils.translation import ugettext_lazy as _

from ella.core.newman_admin import PlacementInlineAdmin, PublishableAdmin,\
    RelatedInlineAdmin
from ella.articles.models import ArticleContents, Article, InfoBox
from ella import newman

class ArticleContentInlineAdmin(newman.NewmanTabularInline):
    model = ArticleContents
    max_num = 1
    rich_text_fields = {None: ('content',)}
    fieldsets = (('', {'fields': ('content',)}),)

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
        (_("Perex"), {'fields': ('description',)}),
    )

    inlines = [ArticleContentInlineAdmin, PlacementInlineAdmin, RelatedInlineAdmin]


newman.site.register(InfoBox, InfoBoxAdmin)
newman.site.register(Article, ArticleAdmin)

