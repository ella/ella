import re
from datetime import datetime
import calendar
import sys
import locale
import codecs

from django.db import models, transaction, connection
from django.contrib import admin
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from ella.core.box import Box
from ella.core.cache.utils import get_cached_object_or_404
from ella.photos.models import Photo
from ella.core.models import Category


ELLA_IMPORT_COUNT = 10
PHOTO_REG = re.compile(r'<img[^>]*src="(?P<url>http://[^"]*)"')

# be able to redirect any non-ascii prints
sys.stdout = codecs.getwriter(locale.getdefaultlocale()[1])(sys.__stdout__)


class Server(models.Model):
    title = models.CharField(_('Title'), max_length=100)
    domain = models.URLField(_('Domain'), verify_exists=False)
    slug = models.CharField(db_index=True, max_length=100)
    url = models.URLField(_('Atom URL'), verify_exists=False, max_length=300)
    category = models.ForeignKey(Category, blank=True, null=True, verbose_name=_('Category'))

    def regenerate (self):
        return mark_safe(u'<a href="%s/fetch/">%s - %s</a>' % (self.id, _('Fetch'), self.title))
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

    def get_from_category(self):
        from ella.core.models import Listing
        from ella.articles.models import Article
        models = [ Article, ]
        articles = Listing.objects.get_listing(category=self.category, count=ELLA_IMPORT_COUNT, mods=models)
        output = {
            'status':200,
            'entries':[]
}
        # Get structure like a feed
        for entry in articles:
            photo_url = ''
            if entry.target.photo:
                photo = entry.target.photo
            else:
                photo = None

            output['entries'].append(
                {
                    'title': entry.target.title,
                    'link': entry.target.get_absolute_url(),
                    'updated': entry.target.updated,
                    'summary': entry.target.perex,
                    'photo_url': photo_url,
                    'photo': photo,
}
)
        return output

    def get_from_feed(self):
        try:
            import feedparser
        except ImportError:
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured, "You must have feedparser installed in order to use automated imports."

        output = feedparser.parse(self.url)
        # repair and set some part of feed
        for entry in output['entries']:
            entry['updated'] = datetime.utcfromtimestamp(calendar.timegm(entry['updated_parsed']))
            img = PHOTO_REG.findall(entry.summary)
            entry['photo_url'] = img[0]
            entry['photo'] = None

        return output

    @transaction.commit_on_success
    def fetch(self):
        if self.category:
            output = self.get_from_category()
        else:
            output = self.get_from_feed()

        importlen =  len(output['entries'])
        if output['status'] == 200 and importlen > 0:
            # for all articles in last but not in this import reset priority to 0
            cursor = connection.cursor()
            cursor.execute(
                    'UPDATE %(table)s SET %(priority)s = 0 WHERE %(priority)s > 0 AND %(server)s = %%s' % {
                        'table' : connection.ops.quote_name(ServerItem._meta.db_table),
                        'priority' : connection.ops.quote_name(ServerItem._meta.get_field('priority').column),
                        'server' : connection.ops.quote_name(ServerItem._meta.get_field('server').column),
},
                    (self.id,)
)
            for index in range(importlen):
                e = output['entries'][index]
                si, created = ServerItem.objects.get_or_create(
                    server=self,
                    link=e['link'],
                    defaults={
                        'priority': importlen - index,
                        'title' : e['title'],
                        'updated' : e['updated'],
                        'summary' : e['summary'],
                        'photo_url': e['photo_url'],
                        'photo': e['photo']
}
)
                # repair priority if needed
                if not created and si.priority >= 0:
                    # unwanted import item has negative priority - never more update priority
                    si.priority = importlen - index
                    si.save()

class ServerItem(models.Model):
    server = models.ForeignKey(Server)
    title = models.CharField(_('Title'), max_length=100)
    summary = models.TextField(_('Summary'))
    updated = models.DateTimeField(_('Updated'))
    priority = models.IntegerField(_('Priority'), default = 0)
    slug = models.CharField(db_index=True, max_length=100)
    link = models.URLField(_('Link'), verify_exists=True, max_length=400)
    photo_url = models.URLField(_('Image URL'), verify_exists=False, max_length=400, blank=True)
    photo = models.ForeignKey(Photo, blank=True, null=True, verbose_name=_('Photo'))

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

        # try and parse photo
        if not self.photo_url:
            img = PHOTO_REG.findall(self.summary)
            if img:
                self.photo_url = img[0]

        if self.photo_url and not self.photo and not self.server.category:
            import urllib
            image = urllib.urlopen(self.photo_url)
            image_raw = image.read()
            image.close()
            imported_photo = Photo()
            imported_photo.title = self.title
            imported_photo.slug = self.slug
            imported_photo.description = self.photo_url
            # FIXME Correct extension of downloaded file
            imported_photo.save_image_file('imported.jpg', image_raw)
            imported_photo.save()
            self.photo = imported_photo

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
    raw_id_fields = ('photo',)

def fetch_all():
    error_count = 0
    for server in Server.objects.all():
        try:
            server.fetch()
            print "OK %s " % (server.title,)
        except Exception, e:
            error_count = error_count + 1
            print "KO %s - %s" % (server.title, e)
    return error_count

admin.site.register(Server, ServerOptions)
admin.site.register(ServerItem, ServerItemOptions)

