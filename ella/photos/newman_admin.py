from django.utils.translation import ugettext_lazy as _
from django.conf.urls.defaults import patterns, url

from ella import newman

from ella.photos.models import FormatedPhoto, Format, Photo
from ella.newman.utils import JsonResponse, JsonResponseError
from ella.newman.conf import newman_settings
from ella.newman.filterspecs import CustomFilterSpec
from ella.newman.licenses.models import License

class PhotoSizeFilter(CustomFilterSpec):

    lookup_w = 'width'
    lookup_h = 'height'

    def title(self):
        return _('Size')

    def get_lookup_kwarg(self):
        return [
            '%s__gt' % self.lookup_w,
            '%s__gt' % self.lookup_h
        ]

    def filter_func(self):
        for size in (100, 150, 200, 300, 500, 600, 700, 800):
            lookup_dict = {
                '%s__gt' % self.lookup_w : size,
                '%s__gt' % self.lookup_h : size
            }
            link_txt = "> %s" % size
            link = (link_txt, lookup_dict)
            self.links.append(link)
        return True

    def generate_choice(self, **lookup_kwargs):
        keys = self.get_lookup_kwarg()
        for key in keys:
            if key in lookup_kwargs:
                return u'>%spx' % lookup_kwargs[key]


class FormatAdmin(newman.NewmanModelAdmin):
    list_display = ('name', 'max_width', 'max_height', 'stretch', 'resample_quality',)
    list_filter = ('sites', 'stretch', 'nocrop', 'flexible_height',)
    search_fields = ('name',)

class FormatedPhotoInlineAdmin(newman.NewmanTabularInline):
    model = FormatedPhoto

def photo_get_list_display():
    if License._meta.installed:
        return ('title', 'size', 'thumb', 'license_info', 'pk',)
    return ('title', 'size', 'thumb', 'pk',)

class PhotoAdmin(newman.NewmanModelAdmin):
    list_display = photo_get_list_display()
    list_filter = ('created',)
    unbound_list_filter = (PhotoSizeFilter,)
    search_fields = ('title', 'slug', 'id',)
    suggest_fields = {'authors': ('name', 'slug',), 'source': ('name', 'url',)}
    rich_text_fields = {'small': ('description',)}

    fieldsets = (
        (_("Heading"), {'fields': ('title',)}),
        (_("Description"), {'fields': ('description',)}),
        (_("Metadata"), {'fields': ('authors', 'source', 'image',)}),
        (_("Important area"), {'fields': (('important_top', 'important_right'), ('important_bottom', 'important_left'),), 'classes': ('collapsed',)})
    )

    def size(self, obj):
        return "%dx%d px" % (obj.width, obj.height)
    size.short_description = _('Size')

    def license_info(self, obj):
        if not License._meta.installed:
            return "---"
        try:
            license = License.objects.get(ct=self.model_content_type, obj_id=obj.id)
        except License.DoesNotExist:
            return '---'
        return u"%sx (%s)" % (license.max_applications, license.note)
    license_info.short_description = _('Max applications')


    def get_urls(self):
        urlpatterns = patterns('',
            url(r'^(\d+)/thumb/$',
                self.json_photo_info,
                name='photo-json-info'),
        )
        urlpatterns += super(PhotoAdmin, self).get_urls()
        return urlpatterns

    def json_photo_info(self, request, object_id, extra_context=None):
        obj = self.get_change_view_object(object_id)

        if obj is None:
            return JsonResponseError(_('Photo id %s does not exists.') % object_id, status=newman_settings.STATUS_OBJECT_NOT_FOUND)

        out = {
            'title': obj.title,
            'thumb_url': obj.thumb_url()
        }

        return JsonResponse('', out)


class FormatedPhotoAdmin(newman.NewmanModelAdmin):
    list_display = ('image', 'format', 'width', 'height')
    list_filter = ('format',)
    search_fields = ('image',)
    raw_id_fields = ('photo',)


newman.site.register(Format, FormatAdmin)
newman.site.register(Photo, PhotoAdmin)
newman.site.register(FormatedPhoto, FormatedPhotoAdmin)

