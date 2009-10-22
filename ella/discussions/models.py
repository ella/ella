from datetime import datetime
from datetime import timedelta
import unicodedata
import logging

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe

from ella.core.models import Category
from ella.core.cache.utils import CachedGenericForeignKey
from ella.core.models import Publishable
from ella.oldcomments.models import Comment
from ella.photos.models import Photo
from ella.discussions.managers import TopicThreadManager

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


ACTIVITY_PERIOD = 6  # Thread activity (hours)


class DuplicationError(Exception):
    pass

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

class Topic(Publishable):
    # ella fields
    created = models.DateTimeField(_('Created'), default=datetime.now, editable=False)

    def __unicode__(self):
        return self.title

    def photo_thumb(self):
        """ Displays Topic photo thumbnail in admin. """
        out = self.photo.thumb()
        return mark_safe(out)
    photo_thumb.allow_tags = True

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

    def get_text(self):
        return ''

    class Meta:
        verbose_name = _('Topic')
        verbose_name_plural = _('Topics')
        ordering = ('-created',)

class PostViewed(models.Model):
    """ posts viewed by user """
    # TODO rename and reside the model. It should be called ItemViewed or something like that.
    target_ct = models.ForeignKey(ContentType, verbose_name=_('Target content type'))
    target_id = models.PositiveIntegerField(_('Target id'))
    target = CachedGenericForeignKey(ct_field="target_ct", fk_field="target_id")

    user = models.ForeignKey(User)

    def __unicode__(self):
        return '%s viewed by %s' % (self.target.__unicode__(), self.user.username)

    def save(self, force_insert=False, force_update=False):
        pv = PostViewed.objects.filter(target_ct=self.target_ct, target_id=self.target_id, user=self.user)
        if pv:
            raise Exception('PostViewed object already exists for ct=%s target_id=%d user=%s' % \
            (str(self.target_ct), self.target_id, self.user))
        super(PostViewed, self).save(force_insert, force_update)

class TopicThread(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=255)
    created = models.DateTimeField(_('Created'), default=datetime.now, editable=False)
    author = models.ForeignKey(User, verbose_name=_('authorized author'), null=True, blank=True)
    nickname = models.CharField(_("Anonymous author's nickname"), max_length=50, blank=True)
    email = models.EmailField(_('Authors email (optional)'), blank=True)
    topic = models.ForeignKey(Topic)
    hit_counts = models.PositiveIntegerField(default=0)

    objects = TopicThreadManager()

    def __init__(self, *args, **kwargs):
        super(TopicThread, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return self.title

    def get_author(self):
        if self.author:
            return self.author.get_full_name()
        return self.nickname

    def get_description(self):
        c = self.posts[self.posts.count()-1]
        return c.content or ''

    def save(self, force_insert=False, force_update=False):
        thr = TopicThread.objects.filter(title=self.title)
        if thr and not self.pk:
            raise DuplicationError('TopicThread with title "%s" already exist.' % self.title)
        super(TopicThread, self).save(force_insert, force_update)

    @property
    def posts(self):
        ctThread = ContentType.objects.get_for_model(TopicThread)
        qset = Comment.objects.filter(target_ct=ctThread)
        return qset.filter(target_id=self.pk)

    def get_absolute_url(self):
        base = self.topic.get_absolute_url()
        return '%s%s/%s/' % (base, slugify(_('posts')), self.slug)

    @property
    def num_posts(self):
        return self.posts.count()

    def get_posts_by_date(self):
        return self.posts.order_by('submit_date')

    def __cmp__(self, other):
        return cmp(self.activity, other.activity)

    def hit(self):
        self.hit_counts += 1
        self.save()

    @property
    def activity(self):
        d = timedelta(hours=ACTIVITY_PERIOD)
        when = datetime.now() - d
        qset = self.get_posts_by_date()
        return qset.filter(submit_date__gte=when).count()

    def last_post(self):
        if not self.posts:
            return ''
        return self.posts.order_by('-submit_date')[0]

    class Meta:
        verbose_name = _('Thread')
        verbose_name_plural = _('Threads')


class BannedString(models.Model):
    expression = models.CharField(_('Expression'), db_index=True, max_length=20)
    isregexp = models.BooleanField(default=False)

    def __unicode__(self):
        return remove_diacritical(self.expression)


class BannedUser(models.Model):
    user = models.ForeignKey(User, related_name='banned_user')

    def __unicode__(self):
        return u'%s' % self.user

log = logging.getLogger('ella.discussions')

