from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from ella.tagging.admin import TaggingInlineOptions

from ella.core.admin import PlacementInlineAdmin, PublishableAdmin
from ella.articles.models import ArticleContents, Article, InfoBox
from ella import newman

class ArticleContentInlineAdmin(newman.NewmanTabularInline):
    model = ArticleContents
    max_num = 1
    rich_text_fields = {None: ('content',)}

class InfoBoxAdmin(newman.NewmanModelAdmin):
    list_display = ('title', 'created',)
    date_hierarchy = 'created'
    list_filter = ('created', 'updated',)
    search_fields = ('title', 'content',)
    rich_text_fields = {None: ('content',)}

class ArticleAdmin(PublishableAdmin):
    ordering = ('-created',)
    fieldsets = (
        (_("Article heading"), {'fields': ('title', 'upper_title', 'updated', 'slug')}),
        (_("Article contents"), {'fields': ('description',)}),
        (_("Metadata"), {'fields': ('category', 'authors', 'source', 'photo')}),
    )
    inlines = [ ArticleContentInlineAdmin, PlacementInlineAdmin ]


admin.site.register(InfoBox, InfoBoxAdmin)
admin.site.register(Article, ArticleAdmin)
