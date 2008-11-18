from django.contrib import admin

from ella.ellaadmin.options import EllaAdminOptionsMixin
from ella.media.models import Media, Section, Usage
from ella.media.forms import MediaForm

class SectionInline(admin.TabularInline):
    model = Section
    extra = 5

class UsageInline(admin.TabularInline):
    model = Usage

class MediaOptions(EllaAdminOptionsMixin, admin.ModelAdmin):

    def __init__(self, *args, **kwargs):
        super(MediaOptions, self).__init__(*args, **kwargs)
        self.form = MediaForm

    prepopulated_fields = {'slug' : ('title',)}

    list_display = ('title',)
    list_filter = ('created', 'updated',)
    search_fields = ('title', 'slug', 'description', 'content',)

#    inlines = (PlacementInlineOptions, TaggingInlineOptions, SectionInline)
    inlines = (SectionInline, UsageInline)

    rich_text_fields = {None: ('description', 'text',)}


admin.site.register(Media, MediaOptions)

