import logging

from django import http
from django.conf.urls.defaults import patterns, url
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from ella import newman
from ella.imports.models import Server, ServerItem

logger = logging.getLogger("ella.imports")

class ServerAdmin(newman.NewmanModelAdmin):
    list_display = ('title', 'domain', 'url', 'regenerate')
    search_fields = ('domain, title', 'url',)
    prepopulated_fields = {'slug' : ('title',)}

    actions = ['a_fetch_servers']

    def a_fetch_servers(self, request, queryset):
        failures = []
        for server in queryset:
            try:
                server.fetch()
            except Exception, e:
                failures.append('Fetch "%s" fail (%s)' % (server, e))
        if failures:
            self.message_user(request, ', '.join(failures))
    a_fetch_servers.short_description = _('Fetch selected servers')

    def get_urls(self):
        urls = patterns('',
            url(r'^(.+)/fetch/$',
                self.fetch_view,
                name='server-fetch'),
        )
        urls += super(ServerAdmin, self).get_urls()
        return urls

    def fetch_view(self, request, pk, extra_context=None):
        server = get_object_or_404(Server, pk=pk)
        try:
            server.fetch()
            return http.HttpResponse('OK')
        except Exception, e:
            return http.HttpResponse('KO ' + str(e))

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'category':
            kwargs['required'] = False
        return super(ServerAdmin, self).formfield_for_dbfield(db_field, **kwargs)

class ServerItemAdmin(newman.NewmanModelAdmin):
    list_display = ('title', 'server', 'updated','priority')
    list_filter = ('server', 'updated',)
    raw_id_fields = ('photo',)

    actions = []


newman.site.register(Server, ServerAdmin)
newman.site.register(ServerItem, ServerItemAdmin)

