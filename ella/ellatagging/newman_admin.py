from ella import newman
from tagging.models import TaggedItem, Tag

class TaggingInlineAdmin(newman.GenericTabularInline):
    model = TaggedItem
    max_num = 3
    ct_field = 'content_type'
    ct_fk_field = 'object_id'
    suggest_fields = {'tag': ('name',)}

class TagAdmin(newman.NewmanModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )

class TaggedItemAdmin(newman.NewmanModelAdmin):
    list_display = ('object', 'tag',)
    list_filter = ('content_type',)
    search_fields = ('tag',)
    suggest_fields = {'tag': ('name',)}

newman.site.register(Tag, TagAdmin)
newman.site.register(TaggedItem, TaggedItemAdmin)
newman.site.append_inline(newman.config.TAGGED_MODELS, TaggingInlineAdmin)

