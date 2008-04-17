from datetime import datetime
from datetime import timedelta
import unicodedata
import logging

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe

from ella.core.models import Listing, Category
from ella.core.cache import get_cached_object
from ella.core.box import Box
from ella.db.models import Publishable
from ella.comments.models import Comment
from ella.photos.models import Photo

"""
HOWTO:
=== Prispevky uzivatele ===
usr=User.objects.get(username='testjf')
ctThread = ContentType.objects.get_for_model(TopicThread)
usr.comment_set.filter(target_ct=ctThread)


=== Vypis vlaken tematu ===
qset = TopicThread.objects.filter(topic=Topic.objects.get(pk=1))


=== Prispevky vlakna ===
qset = Comment.objects.filter(target_ct=ctThread)
qset.filter(target_id=2)  # 2 .. id threadu
     nebo:
thr = TopicThread.objects.get(pk=1)
Comment.objects.get_list_for_object(thr)


=== Setrideni prispevku vlakna ===
(nejprve ziskat QuerySet s prispevky (podle uzivatele, vlakna, ...))
qset.order_by('submit_date')
     posledni prisp.:
qset.latest('submit_date')


=== URL prispevk. formulare ===
http://localhost:8000/testovaci-kategorie/2008/3/28/temata/prvni-pomoc/dotaz/

Poznamky k registraci:
http://www.b-list.org/weblog/2006/sep/02/django-tips-user-registration/
"""

"""
TODO 2008-04-16:
1. prihlaseny admin - muze kliknout na IDcko.

2. profil Zaneta posle (polozky)

3. Sherlock -- pripravit export (zeptat se Ondry na detaily)

4. poradny - podivat se na atlas.cz
   - otazky posilaj ianon. uzivatele
   - otazky nejsou hned videt na webu
   - videt jsou zodpovezene otazky + odpovedi.
   - po kliknuti na odpoved odbornika, bude stranka s odpovedi + komentari uzivatelu.
"""

ACTIVITY_PERIOD = 6  # Thread activity (hours)


def get_comments_on_thread(thread):
    ctThread = ContentType.objects.get_for_model(TopicThread)
    qset = Comment.objects.filter(target_ct=ctThread)
    return qset.filter(target_id=thread.id)

def remove_diacritical(text):
    line = unicodedata.normalize('NFKD', text)
    output = ''
    for c in line:
        if not unicodedata.combining(c):
            output += c
    return output

class Topic(models.Model, Publishable):
    # ella fields
    title = models.CharField(_('Title'), max_length=255)
    description = models.TextField(_('Description'))
    slug = models.CharField(_('Slug'), db_index=True, max_length=255)
    category = models.ForeignKey(Category, verbose_name=_('Category'))
    photo = models.ForeignKey(Photo, blank=True, null=True, verbose_name=_('Photo'))
    created = models.DateTimeField(_('Created'), default=datetime.now, editable=False)

    def __unicode__(self):
        return self.title

    @property
    def main_listing(self):
        try:
            return get_cached_object(
                    Listing,
                    target_ct=ContentType.objects.get_for_model(self.__class__),
                    target_id=self.id,
                    category=self.category_id
)
        except Listing.DoesNotExist:
            return None

    def get_absolute_url(self):
        listing = self.main_listing
        if listing:
            return listing.get_absolute_url()

    def photo_thumb(self):
        """ Displays Topic photo thumbnail in admin. """
        # TODO odstranit absolutni URL - bylo jen k rychlemu testu
        out = '<img src="http://dev11.netcentrum.cz:8060/static/photos/2008/03/11/thumb-131293-pivoo.jpg" alt=""/>'
        out = self.photo.thumb()
        return mark_safe(out)
    photo_thumb.allow_tags = True

    @property
    def get_description(self):
        return self.description

    def get_threads(self):
        return TopicThread.objects.filter(topic=self)

    def get_threads_by_date(self):
        return self.get_threads().order_by('-created')

    def get_threads_by_activity(self):
        act = {}
        for t in self.get_threads_by_date().order_by('created'):
            act[t] = t.activity
        tmp = act.items()
        tmp = [(v, k) for (k, v) in tmp]
        tmp.sort()
        tmp.reverse()
        tmp = [(k, v) for (v, k) in tmp]
        out = [key for key, value in tmp]
        return out

    def get_threads_by_view(self):
        """ returns the most viewed threads """
        return None

    class Meta:
        verbose_name = _('Topic')
        verbose_name_plural = _('Topics')
        ordering = ('-created',)


class TopicThread(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    slug = models.CharField(_('Slug'), db_index=True, max_length=255)
    created = models.DateTimeField(_('Created'), default=datetime.now, editable=False)
    author = models.ForeignKey(User, verbose_name=_('authorized author'),)
    topic = models.ForeignKey(Topic)
    # TODO (NAVSTEVNOST) hit count? Should be automatic by Ella (?) - prove it.

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.__posts = []

    def __unicode__(self):
        return self.title

    def __load_posts(self):
        if self.__posts:
            return
        ctThread = ContentType.objects.get_for_model(TopicThread)
        qset = Comment.objects.filter(target_ct=ctThread)
        self.__posts = qset.filter(target_id=self.pk)

    def get_absolute_url(self):
        base = self.topic.get_absolute_url()
        return '%s%s/%s' % (base, slugify(_('posts')), self.slug)

    @property
    def num_posts(self):
        self.__load_posts()
        return self.__posts.count()

    def get_posts_by_date(self):
        self.__load_posts()
        return self.__posts.order_by('submit_date')

    def __cmp__(self, other):
        return cmp(self.activity, other.activity)

    @property
    def activity(self):
        d = timedelta(hours=ACTIVITY_PERIOD)
        when = datetime.now() - d
        qset = self.get_posts_by_date()
        return qset.filter(submit_date__gte=when).count()

    def last_post(self):
        self.__load_posts()
        # FIXME check list length, sort by date to get the latest item.
        if not self.__posts:
            return ''
        return self.__posts.order_by('-submit_date')[0]

    class Meta:
        verbose_name = _('Thread')
        verbose_name_plural = _('Threads')
        ordering = ('title',)


class BannedString(models.Model):
    expression = models.CharField(_('Expression'), db_index=True, max_length=20)
    isregexp = models.BooleanField(default=False)

    def __unicode__(self):
        return remove_diacritical(self.expression)


class BannedUser(models.Model):
    user = models.ForeignKey(User, related_name='banned_user')

    def __unicode__(self):
        return self.user



# initialization
from ella.discussions import register
del register

log = logging.getLogger('ella.discussions')
