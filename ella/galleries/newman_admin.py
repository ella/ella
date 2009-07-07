from django.utils.translation import ugettext_lazy as _

from ella import newman

from ella.galleries.models import Gallery, GalleryItem
from ella.core.newman_admin import PlacementInlineAdmin, PublishableAdmin


class GalleryItemInline(newman.options.NewmanInlineModelAdmin):
    template = 'newman/edit_inline/gallery_item.html'
    model = GalleryItem
    extra = 1

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'target_ct':
            kwargs.update({
                'widget': newman.widgets.GalleryItemContentTypeWidget
            })
            if 'request' in kwargs:
                del(kwargs['request'])
            return db_field.formfield(**kwargs)
        return super(GalleryItemInline, self).formfield_for_dbfield(db_field, **kwargs)


class GalleryAdmin(PublishableAdmin):
    ordering = ('-created',)
    fieldsets = (
        (_("Heading"), {'fields': ('title', 'slug',)}),
        (_("Content"), {'fields': ('description', 'content',)}),
        (_("Metadata"), {'fields': ('authors', 'category')}),
)
    list_filter = ('created', 'category',)
    search_fields = ('title', 'description', 'slug',)
    inlines = [GalleryItemInline, PlacementInlineAdmin]
    rich_text_fields = {'small': ('description',), None: ('content',)}
    prepopulated_fields = {'slug': ('title',)}

newman.site.register(Gallery, GalleryAdmin)

