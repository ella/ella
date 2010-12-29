from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from ella.core.admin import PublishableAdmin, PlacementForm
from ella.core.models import Placement
from ella.articles.models import ArticleContents, Article, InfoBox
from ella.ellaadmin.options import EllaAdminOptionsMixin, EllaModelAdmin, EllaAdminInline

class ArticleContentInlineAdmin(EllaAdminInline, admin.TabularInline):
    model = ArticleContents
    max_num = 1
    rich_text_fields = {None: ('content',)}

class InfoBoxAdmin(EllaAdminOptionsMixin, EllaModelAdmin):
    list_display = ('title', 'created',)
    date_hierarchy = 'created'
    list_filter = ('created', 'updated',)
    search_fields = ('title', 'content',)
    rich_text_fields = {None: ('content',)}

class PlacementInlineAdmin(admin.TabularInline):
    exclude = ('slug',)
    model = Placement
    max_num = 1
    suggest_fields = {'category': ('__unicode__', 'title', 'slug',)}
    
    form = PlacementForm

class ArticleAdmin(PublishableAdmin):
    ordering = ('-created',)
    fieldsets = (
        (_("Article heading"), {'fields': ('title', 'upper_title', 'updated', 'slug')}),
        (_("Article contents"), {'fields': ('description',)}),
        (_("Metadata"), {'fields': ('category', 'authors', 'source', 'photo')}),
    )
    inlines = [ArticleContentInlineAdmin, PlacementInlineAdmin]


admin.site.register(InfoBox, InfoBoxAdmin)
admin.site.register(Article, ArticleAdmin)
