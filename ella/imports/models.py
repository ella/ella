import re
from datetime import datetime
import calendar

from django.db import models, transaction, connection
from django.contrib import admin
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _

from ella.core.box import Box
from ella.core.cache.utils import get_cached_object_or_404

class Server(models.Model):
    title = models.CharField(_('Title'), maxlength=100)
    domain = models.URLField(_('Domain'), verify_exists=False)
    slug = models.CharField(db_index=True, maxlength=100)
    url = models.URLField(_('Atom URL'), verify_exists=False, max_length=300)


    def regenerate (self):
        return u'<a href="%s/fetch/">%s - %s</a>' % (self.id, _('Fetch'), self.title)
    regenerate.allow_tags = True

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Server')
        verbose_name_plural = _('Servers')
        ordering = ('title',)

    def get_imports_by_time(self):
        return self.serveritem_set.order_by("-updated")

    def get_imports_by_priority(self):
        return self.serveritem_set.order_by("-priority", "-updated")

    @transaction.commit_on_success
    def fetch(self):
        try:
            import feedparser
        except ImportError:
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured, "You must have feedparser installed in order to use automated imports."

        output = feedparser.parse(self.url)
        if output['status'] == 200:
            # for all articles in last but not in this import reset priority to 0
            cursor = connection.cursor()
            cursor.execute(
                    'UPDATE %(table)s SET %(priority)s = 0 WHERE %(priority)s > 0' % {
                        'table' : connection.ops.quote_name(self._meta.db_table),
                        'priority' : connection.ops.quote_name(self._meta.get_field('priority')),
},
                    []
)
            importlen =  len(output['entries'])
            for index in range(importlen):
                e = output['entries'][index]
                si, created = ServerItem.objects.get_or_create(
                    server=self,
                    link=e['link'],
                    defaults={
                        'priority': importlen - index,
                        'title' : e['title'],
                        'updated' : datetime.utcfromtimestamp(calendar.timegm(e['updated_parsed'])),
                        'summary' : e['summary'],
}
)
                # repair priority if needed
                if not created and si.priority >= 0:
                    # unwanted import item has negative priority - never more update priority
                    si.priority = importlen - index
                    si.save()

PHOTO_REG = re.compile(r'<img[^>]*src="(?P<url>http://[^"]*)"')

class ServerItem(models.Model):
    server = models.ForeignKey(Server)
    title = models.CharField(_('Title'), maxlength=100)
    summary = models.TextField(_('Summary'))
    updated = models.DateTimeField(_('Updated'))
    priority = models.IntegerField(_('Priority'), default = 0)
    slug = models.CharField(db_index=True, maxlength=100)
    link = models.URLField(_('Link'), verify_exists=True, max_length=400)
    photo_url = models.URLField(_('Image URL'), verify_exists=False, max_length=400, blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Server item')
        verbose_name_plural = _('Server items')
        ordering = ('-updated',)
        unique_together = (('server', 'slug',),)

    def save(self):
        from django.template.defaultfilters import slugify
        if not self.slug:
            slug = slugify(self.title)
            try:
                ServerItem.objects.get(server=self.server, slug=slug)
            except ServerItem.DoesNotExist:
                pass
            else:
                base_slug = slug + '-'
                i = 0
                while True:
                    slug = base_slug + str(i)
                    i += 1
                    try:
                        ServerItem.objects.get(server=self.server, slug=slug)
                    except ServerItem.DoesNotExist:
                        break
            self.slug = slug

        # try andparse photo
        if not self.photo_url:
            img = PHOTO_REG.findall(self.summary)
            if img:
                self.photo_url = img[0]

        self.summary = strip_tags(self.summary)

        super(ServerItem, self).save()


class ServerOptions(admin.ModelAdmin):
    list_display = ('title', 'domain', 'url', 'regenerate')
    search_fields = ('domain, title', 'url',)
    prepopulated_fields = {'slug' : ('title',)}

    def __call__(self, request, url):
        if url and url.endswith('fetch'):
            from django import http
            pk = url.split('/')[-2]
            server = get_cached_object_or_404(Server, pk=pk)
            try:
                server.fetch()
                return http.HttpResponse('OK')
            except Exception, e:
                return http.HttpResponse('KO ' + str(e))

        return super(ServerOptions, self).__call__(request, url)


class ServerItemOptions(admin.ModelAdmin):
    list_display = ('title', 'server', 'updated','priority')
    list_filter = ('server', 'updated',)

admin.site.register(Server, ServerOptions)
admin.site.register(ServerItem, ServerItemOptions)

