from django.contrib import admin
from django import http

from ella.core.cache.utils import get_cached_object_or_404

from ella.imports.models import Server, ServerItem

from ella.ellaadmin.options import EllaAdminOptionsMixin

class ServerOptions(EllaAdminOptionsMixin, admin.ModelAdmin):
    list_display = ('title', 'domain', 'url', 'regenerate')
    search_fields = ('domain, title', 'url',)
    prepopulated_fields = {'slug' : ('title',)}

    def __call__(self, request, url):
        """Defines "*/fetch" page which starts the import procedure and shows the result status."""
        if url and url.endswith('fetch'):
            pk = url.split('/')[-2]
            server = get_cached_object_or_404(Server, pk=pk)
            try:
                server.fetch()
                return http.HttpResponse('OK')
            except Exception, e:
                return http.HttpResponse('KO ' + str(e))

        return super(ServerOptions, self).__call__(request, url)

class ServerItemOptions(EllaAdminOptionsMixin, admin.ModelAdmin):
    list_display = ('title', 'server', 'updated','priority')
    list_filter = ('server', 'updated',)
    raw_id_fields = ('photo',)


admin.site.register(Server, ServerOptions)
admin.site.register(ServerItem, ServerItemOptions)

