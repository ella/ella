from django.contrib import admin
from django.contrib.contenttypes import generic
from ella.tagging.models import Tag, TaggedItem

class TaggingInlineOptionsSimple(admin.TabularInline):
    model = TaggedItem
    extra = 0

class TaggingInlineOptions(generic.GenericTabularInline):
    raw_id_fields = ('tag',)
    model = TaggedItem
    extra = 4
    id_field_name = 'object_id'
    ct_field_name = 'content_type'

    def formfield_for_dbfield(self, db_field, **kwargs):
        from ella.tagging.fields import SuggestTagAdminField
        if db_field.name == 'tag':
            return SuggestTagAdminField(db_field, **kwargs)
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)

class TagOptions(admin.ModelAdmin):
    """
    Grrrrr
    """
    ordernig = ('name',)
    list_display = ('name',)
    inlines = (TaggingInlineOptionsSimple,)
    search_fields = ('name',)

class TaggedItemOptions(admin.ModelAdmin):
    """
    Uaaarghhh
    """
    list_display = ('tag', 'content_type',)

admin.site.register(Tag, TagOptions)
admin.site.register(TaggedItem, TaggedItemOptions)


