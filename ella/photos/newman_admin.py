from django.conf.urls.defaults import patterns, url
from django.contrib.admin import helpers
from django.contrib.admin.util import flatten_fieldsets
from django.contrib.csrf.middleware import csrf_exempt
from django.contrib.sites.models import Site
from django.forms.models import modelform_factory
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.functional import curry
from django.utils.translation import ugettext_lazy as _

import ella_newman as newman

from ella.photos.models import FormatedPhoto, Format, Photo
from ella_newman.utils import JsonResponse, JsonResponseError
from ella_newman.conf import newman_settings
from ella_newman.filterspecs import CustomFilterSpec

from django import forms

# Flash image uploader / editor
CSS_UPLOADIFY_LIB = 'css/uploadify.css'
JS_SWFOBJECT = 'js/swfobject.js'
JS_UPLOADIFY_LIB = 'js/jquery.uploadify.min.js'
SWF_FLASH_UPLOADER = 'swf/uploadify.swf'


class MassUploadForm(forms.ModelForm):
    image_file = forms.ImageField(label=_('Image files'))


    class Media:
        js = (
            newman_settings.MEDIA_PREFIX + JS_SWFOBJECT,
            newman_settings.MEDIA_PREFIX + JS_UPLOADIFY_LIB,
            newman_settings.MEDIA_PREFIX + SWF_FLASH_UPLOADER,
            )
        css = {
            'screen': (newman_settings.MEDIA_PREFIX + CSS_UPLOADIFY_LIB,),
        }


    class Meta:
        model = Photo
        exclude = (
            'image', 'important_top', 'important_left', 'important_bottom',
            'important_right')


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
                '%s__gt' % self.lookup_w: size,
                '%s__gt' % self.lookup_h: size
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
    list_display = (
        'name', 'max_width', 'max_height', 'stretch', 'resample_quality',)
    list_filter = ('sites', 'stretch', 'nocrop', 'flexible_height',)
    search_fields = ('name',)


class FormatedPhotoInlineAdmin(newman.NewmanTabularInline):
    model = FormatedPhoto


class PhotoAdmin(newman.NewmanModelAdmin):
    list_display = ('title', 'size', 'thumb', 'pk',)
    list_filter = ('created',)
    unbound_list_filter = (PhotoSizeFilter,)
    search_fields = ('title', 'slug', 'id',)
    suggest_fields = {'authors': ('name', 'slug',),
                      'source': ('name', 'url',)}
    rich_text_fields = {'small': ('description',)}

    fieldsets = (
        (_("Heading"), {'fields': ('title',)}),
        (_("Description"), {'fields': ('description',)}),
        (_("Metadata"), {'fields': ('authors', 'source', 'image',)}),
        (_("Important area"), {'fields': (
            ('important_top', 'important_right'),
            ('important_bottom', 'important_left'),), 'classes': ('collapsed',)})
        )
    mass_upload_fieldsets = (
        (_("Heading"), {'fields': ('title',)}),
        (_("Description"), {'fields': ('description',)}),
        (_("Metadata"), {'fields': ('authors', 'source', 'image_file')}),
        )
    mass_upload2_fieldsets = (
        (_("Image Data"),
         {'fields': ('title', 'description', 'authors', 'source')}),
        )

    def size(self, obj):
        return "%dx%d px" % (obj.width, obj.height)

    size.short_description = _('Size')


    def thumb(self, obj):
        """
        Generates html and thumbnails for admin site.
        """
        format, created = Format.objects.get_or_create(name='newman_thumb',
                                                       defaults={
            'max_width': 100,
            'max_height': 100,
            'flexible_height': False,
            'stretch': False,
            'nocrop': True,
        })

        if created:
            format.sites = Site.objects.all()

        info = obj.get_formated_photo(format)

        return '<a href="%(href)s"><img src="%(src)s"></a>' % {
            'href': '%s/' % obj.pk,
            'src': info['url']
        }
    thumb.allow_tags = True


    def get_urls(self):
        urlpatterns = patterns('',
                               url(r'^(\d+)/thumb/$', self.json_photo_info,
                                   name='photo-json-info'),
                               url(r'^mass-upload/upload-file/$',
                                   self.upload_file_view,
                                   name='photo-mass-upload-file'),
                               url(r'^mass-upload/$', self.mass_upload_view,
                                   name='photo-mass-upload'),
        )
        urlpatterns += super(PhotoAdmin, self).get_urls()
        return urlpatterns

    def json_photo_info(self, request, object_id, extra_context=None):
        from ella_newman.conf import PHOTOS_THUMB_FORMAT

        obj = self.get_change_view_object(object_id)

        if obj is None:
            return JsonResponseError(
                _('Photo id %s does not exists.') % object_id,
                status=newman_settings.STATUS_OBJECT_NOT_FOUND)

        out = {
            'title': obj.title,
            'thumb_url': obj.get_formated_photo(PHOTOS_THUMB_FORMAT)['url']
        }

        return JsonResponse('', out)

    def get_mass_upload_context(self, request):
        model = self.model
        opts = model._meta
        self.register_newman_variables(request)

        # To enable admin-specific fields, we need to run the form class
        # through modelform_factory using curry
        FormClass = modelform_factory(Photo, form=MassUploadForm,
                                      fields=flatten_fieldsets(
                                          self.mass_upload_fieldsets),
                                      formfield_callback=curry(
                                          self.formfield_for_dbfield,
                                          request=request)
        )

        context = {}
        if request.method == 'POST':
            error_dict = {}
            # Unfortunately, FLASH uploader sends array data in weird format
            # so that Django doesn't recognize it as array of values, but
            # as one string with commas inside. The only way to expect it
            # and preprocess the values by ourselves.
            data = dict((key, val) for key, val in request.POST.items())
            form = FormClass(data, request.FILES)

            if form.is_valid():
                # To prevent newman from handling our field by common flash editor
                # we need to use a different mechanism
                new_object = form.save(commit=False)
                new_object.image = form.cleaned_data['image_file']
                new_object.save()
                form.save_m2m()
                context.update({'object': new_object})
            else:
                for e in form.errors:
                    error_dict[u"id_%s" % e] = [u"%s" % ee for ee in
                                                form.errors[e]]
                context.update({'error_dict': error_dict})
        else:
            form = FormClass()

        adminForm = helpers.AdminForm(form, list(self.mass_upload_fieldsets), self.prepopulated_fields)
        massUploadForm = helpers.AdminForm(form, list(self.mass_upload2_fieldsets), self.prepopulated_fields)
        media = self.media + adminForm.media

        context.update({
            'title': _('Mass upload'),
            'adminform': adminForm,
            'mass_upload2_form': massUploadForm,
            'is_popup': request.REQUEST.has_key('_popup'),
            'show_delete': False,
            'media': media,
            'inline_admin_formsets': [],
            'errors': helpers.AdminErrorList(form, ()),
            'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
            'opts': opts,
            'has_change_permission': self.has_change_permission(request,
                                                                None),
            'raw_form': form
        })
        return context

    @csrf_exempt    # as long as we don't use multipart for fileupload, no chance to send CSRF token along
    def upload_file_view(self, request):
        context = self.get_mass_upload_context(request)
        if 'error_dict' in context:
            return self.json_error_response(request, context)
        else:
            obj = context['object']
            return JsonResponse('', {'object_id': obj.id,
                                     'object_title': obj.title})

    def mass_upload_view(self, request):
        context = self.get_mass_upload_context(request)
        return render_to_response('newman/photos/photo/mass_upload.html',
            context, context_instance=RequestContext(request,
                                                     current_app=self.admin_site.name)
        )


class FormatedPhotoAdmin(newman.NewmanModelAdmin):
    list_display = ('image', 'format', 'width', 'height')
    list_filter = ('format',)
    search_fields = ('image',)
    raw_id_fields = ('photo',)


newman.site.register(Format, FormatAdmin)
newman.site.register(Photo, PhotoAdmin)
newman.site.register(FormatedPhoto, FormatedPhotoAdmin)
