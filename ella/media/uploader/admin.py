from django.contrib import admin

from ella.media.uploader.models import Upload


class UploadOptions(admin.ModelAdmin):
    list_filter = ('type', 'uploaded',)
    search_fields = ('hash', 'title', 'description',)


admin.site.register(Upload, UploadOptions)

