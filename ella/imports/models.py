import re
from datetime import datetime
import calendar
import urllib

from django.db import models, connection
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.template.defaultfilters import slugify
from django.core.files.base import ContentFile

from ella.articles.models import Article
from ella.core.models import Category, Listing


ELLA_IMPORT_COUNT = 10
PHOTO_REG = re.compile(r'<img[^>]*src="(?P<url>http://[^"]*)"')


class Server(models.Model):
    """Import source server"""
    title = models.CharField(_('Title'), max_length=100)
    domain = models.URLField(_('Domain'), verify_exists=False)
    slug = models.SlugField(_('Slug'), max_length=255)
    url = models.URLField(_('Atom URL'), verify_exists=False, max_length=300, blank=True)
    category = models.ForeignKey(Category, blank=True, null=True, verbose_name=_('Category'))

    def regenerate(self):
        """Link to inialize a fetch"""
        return mark_safe(u'<a href="%s/fetch/">%s - %s</a>' % (self.id, _('Fetch'), self.title))
    regenerate.allow_tags = True

    def get_imports_by_time(self):
        return self.serveritem_set.order_by("-updated")

    def get_imports_by_priority(self):
        return self.serveritem_set.order_by("-priority", "-updated")

    def get_from_category(self):
        "Imports from other ella application, which runs on the same database."
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
                    'link': entry.get_domain_url(),
                    'updated': entry.publish_from,
                    'summary': entry.target.description,
                    'photo_url': photo_url,
                    'photo': photo,
                }
            )
        return output

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Server')
        verbose_name_plural = _('Servers')
        ordering = ('title',)


    def get_from_feed(self):
        "Import from the RSS/Atom source."
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
            if img:
                entry['photo_url'] = img[0]
            else:
                entry['photo_url'] = ''
            entry['photo'] = None

        return output

    def fetch(self):
        "Runs the item fetch from the category or feed (based on self.category) and saves them into ServerItem."
        if self.category:
            output = self.get_from_category()
        elif self.url:
            output = self.get_from_feed()
        else:
            return

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
            ServerItem.objects.filter(server=self, priority=0).delete()
        else:
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured('Import Failed')

def _photo_model():
    from ella.photos.models import Photo
    return Photo

class ServerItem(models.Model):
    "Specific item to be imported."

    server = models.ForeignKey(Server)
    title = models.CharField(_('Title'), max_length=100)
    summary = models.TextField(_('Summary'))
    updated = models.DateTimeField(_('Updated'))
    priority = models.IntegerField(_('Priority'), default = 0)
    slug = models.SlugField(_('Slug'), max_length=255)
    link = models.URLField(_('Link'), verify_exists=True, max_length=400)
    photo_url = models.URLField(_('Image URL'), verify_exists=False, max_length=400, blank=True)
    photo = models.ForeignKey(_photo_model(), blank=True, null=True, verbose_name=_('Photo'))

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Server item')
        verbose_name_plural = _('Server items')
        ordering = ('-updated',)
        unique_together = (('server', 'slug',),)

    def save(self, **kwargs):
        """Overrides models.Model.save.

        - Assigns unique slugs to the items.
        - Tries to find and parse photo in summary, in case it isn't defined on the item.
        - Saves copy of item's photo on the local servers. (Feed imports only.)
        """
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
            image = urllib.urlopen(self.photo_url)
            try:
                content_file = ContentFile( image.read() )
            finally:
                image.close()
            imported_photo = _photo_model()()
            imported_photo.title = self.title
            imported_photo.slug = self.slug
            imported_photo.description = self.photo_url
            # Saves "imported.jpg" file, which has been created when importing item with picture
            imported_photo.image.save( 'imported.jpg', content_file )
            imported_photo.save()
            self.photo = imported_photo

        self.summary = strip_tags(self.summary)

        super(ServerItem, self).save(**kwargs)

