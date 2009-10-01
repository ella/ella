from django.conf.urls.defaults import patterns, url
import logging
logger = logging.getLogger("ella.imports")

from ella import newman
from django import http

from ella.core.cache.utils import get_cached_object_or_404

from ella.imports.models import Server, ServerItem

class ServerAdmin(newman.NewmanModelAdmin):
    list_display = ('title', 'domain', 'url', 'regenerate')
    search_fields = ('domain, title', 'url',)
    prepopulated_fields = {'slug' : ('title',)}

    def get_urls(self):
        urls = patterns('',
            url(r'^(.+)/fetch/$',
                self.fetch_view,
                name='server-fetch'),
        )
        urls += super(ServerAdmin, self).get_urls()
        return urls

    def fetch_view(self, request, pk, extra_context=None):
        server = get_cached_object_or_404(Server, pk=pk)
        try:
            server.fetch()
            return http.HttpResponse('OK')
        except Exception, e:
            return http.HttpResponse('KO ' + str(e))

class ServerItemAdmin(newman.NewmanModelAdmin):
    list_display = ('title', 'server', 'updated','priority')
    list_filter = ('server', 'updated',)
    raw_id_fields = ('photo',)


newman.site.register(Server, ServerAdmin)
newman.site.register(ServerItem, ServerItemAdmin)

