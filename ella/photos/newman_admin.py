from django.utils.translation import ugettext_lazy as _

from ella import newman

from ella.photos.models import FormatedPhoto, Format, Photo

class FormatOptions(newman.NewmanModelAdmin):
    list_display = ('name', 'max_width', 'max_height', 'stretch', 'resample_quality',)
    list_filter = ('sites', 'stretch', 'nocrop', 'flexible_height',)
    search_fields = ('name',)

class FormatedPhotoInlineOptions(newman.NewmanTabularInline):
    model = FormatedPhoto

class PhotoOptions(newman.NewmanModelAdmin):
    inlines = []
    list_display = ('title', 'size', 'thumb', 'pk',)
    list_filter = ('created',)
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'image', 'description', 'id',)
    suggest_fields = {'authors': ('name', 'slug',), 'source': ('name', 'url',)}

    def size(self, obj):
        return "%dx%d px" % (obj.width, obj.height)
    size.short_description = _('Size')

class FormatedPhotoOptions(newman.NewmanModelAdmin):
    list_display = ('image', 'format', 'width', 'height')
    list_filter = ('format',)
    search_fields = ('image',)
    raw_id_fields = ('photo',)


newman.site.register(Format, FormatOptions)
newman.site.register(Photo, PhotoOptions)
newman.site.register(FormatedPhoto, FormatedPhotoOptions)

