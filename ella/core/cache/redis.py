from __future__ import absolute_import

import logging
from datetime import date, timedelta
from hashlib import md5
from itertools import chain

from django.conf import settings
from django.db.models.loading import get_model

from ella.core.cache.utils import get_cached_objects, SKIP
from ella.core.managers import ListingHandler
from ella.core.conf import core_settings
from ella.utils.timezone import now, to_timestamp, from_timestamp

log = logging.getLogger('ella.core')

client = None

if hasattr(settings, 'LISTINGS_REDIS'):
    try:
        from redis import Redis
    except:
        log.error('Redis support requested but Redis client not installed.')
        client = None
    else:
        client = Redis(**getattr(settings, 'LISTINGS_REDIS'))



def ListingHandlerClass():
    return get_model('core', 'Listing').objects.get_listing_handler(core_settings.REDIS_LISTING_HANDLER)


def publishable_published(publishable, **kwargs):
    pipe = client.pipeline()
    listings = publishable.listing_set.all()

    for l in listings:
        ListingHandlerClass().add_publishable(
            l.category,
            publishable,
            publish_from=l.publish_from,
            pipe=pipe,
            commit=False
        )

    if len(listings) > 0:
        AuthorListingHandler.add_publishable(publishable, pipe=pipe, commit=False)

    pipe.execute()


def publishable_unpublished(publishable, **kwargs):
    pipe = client.pipeline()
    for l in publishable.listing_set.all():
        ListingHandlerClass().remove_publishable(
            l.category,
            publishable,
            pipe=pipe,
            commit=False
        )

    AuthorListingHandler.remove_publishable(publishable, pipe=pipe, commit=False)
    pipe.execute()


def listing_pre_delete(sender, instance, **kwargs):
    # prepare redis pipe for deletion...
    instance.__pipe = ListingHandlerClass().remove_publishable(
        instance.category,
        instance.publishable,
        commit=False
    )


def listing_post_delete(sender, instance, **kwargs):
    # but only delete it if the model delete went through
    pipe = instance.__pipe
    listings = instance.publishable.listing_set.all()

    if instance.publishable.published:
        for l in listings:
            ListingHandlerClass().add_publishable(
                l.category,
                instance.publishable,
                publish_from=l.publish_from,
                pipe=pipe,
                commit=False
            )

    # If this is the last Listing that is being deleted, delete from author too.
    if not listings.exists():
        AuthorListingHandler.remove_publishable(instance.publishable, pipe=pipe,
                                                commit=False)
    pipe.execute()


def listing_pre_save(sender, instance, **kwargs):
    if instance.pk:
        # prepare deletion of stale data
        old_listing = instance.__class__.objects.get(pk=instance.pk)
        instance.__pipe = ListingHandlerClass().remove_publishable(
            old_listing.category,
            old_listing.publishable,
            commit=False
        )


def listing_post_save(sender, instance, **kwargs):
    pipe = getattr(instance, '__pipe', client.pipeline())

    if instance.publishable.published:
        ListingHandlerClass().add_publishable(
            instance.category,
            instance.publishable,
            publish_from=instance.publish_from,
            pipe=pipe,
            commit=False
        )

        # This is the first listing being added.
        if instance.publishable.listing_set.count() == 1:
            AuthorListingHandler.add_publishable(instance.publishable, pipe=pipe,
                                                 commit=False)

        pipe.execute()


def update_authors(sender, action, instance, reverse, model, pk_set, **kwargs):
    if action == 'pre_remove':
        instance.__pipe = AuthorListingHandler.remove_publishable(instance, commit=False)
    elif action in ('post_remove', 'post_add') and instance.published and instance.listing_set.exists():
        AuthorListingHandler.add_publishable(instance, pipe=getattr(instance, '__pipe', None))

class RedisListingHandler(ListingHandler):
    PREFIX = 'listing'

    @classmethod
    def get_value(cls, publishable):
        return ':'.join((str(publishable.content_type_id), str(publishable.pk)))

    @classmethod
    def get_keys(cls, category, publishable):
        # main category
        keys = [':'.join((cls.PREFIX, str(category.id)))]
        keys.append(':'.join((cls.PREFIX, 'c', str(category.id))))
        keys.append(':'.join((cls.PREFIX, 'd', str(category.id))))

        # content_type
        keys.append(':'.join((cls.PREFIX, 'ct', str(publishable.content_type_id))))

        # category shouldn't be propagated
        if not category.app_data.ella.propagate_listings:
            return keys

        # children
        if category.tree_parent_id:
            keys.append(':'.join((cls.PREFIX, 'c', str(category.tree_parent_id))))

        # all children
        while category.tree_parent_id:
            category = category.tree_parent
            keys.append(':'.join((cls.PREFIX, 'd', str(category.id))))
            if not category.app_data.ella.propagate_listings:
                break

        return keys

    @classmethod
    def add_publishable(cls, category, publishable, score, pipe=None, commit=True):
        if pipe is None:
            pipe = client.pipeline()

        for k in cls.get_keys(category, publishable):
            pipe.zadd(k, cls.get_value(publishable), score)

        if commit:
            pipe.execute()
        else:
            return pipe

    @classmethod
    def incr_score(cls, category, publishable, incr_by=1, pipe=None, commit=True):
        if pipe is None:
            pipe = client.pipeline()

        v = cls.get_value(publishable)
        for k in cls.get_keys(category, publishable):
            pipe.zincrby(k, v, incr_by)

        if commit:
            pipe.execute()
        else:
            return pipe

    @classmethod
    def remove_publishable(cls, category, publishable, pipe=None, commit=True):
        if pipe is None:
            pipe = client.pipeline()

        for k in cls.get_keys(category, publishable):
            pipe.zrem(k, cls.get_value(publishable))

        if commit:
            pipe.execute()
        else:
            return pipe

    def count(self):
        key, pipe = self._get_key()
        if pipe is None:
            pipe = client.pipeline()
        pipe = pipe.zcard(key)
        results = pipe.execute()
        return results[-1]

    def _get_listing(self, publishable, score):
        Listing = get_model('core', 'listing')
        return Listing(publishable=publishable, category=publishable.category)

    def _get_score_limits(self):
        max_score = None
        min_score = None

        if self.date_range:
            raise NotImplemented()
        return min_score, max_score

    def get_listings(self, offset=0, count=10):
        key, pipe = self._get_key()
        if pipe is None:
            pipe = client.pipeline()

        # get the score range based on the date range
        min_score, max_score = self._get_score_limits()

        # get all the relevant records
        if min_score or max_score:
            pipe = pipe.zrevrangebyscore(key,
                max_score, min_score,
                start=offset, num=count,
                withscores=True
            )
        else:
            pipe = pipe.zrevrange(key,
                start=offset, end=offset + count - 1,
                withscores=True
            )
        results = pipe.execute()

        # get the data from redis into proper format
        data = []
        ids = []
        for value, score in results[-1]:
            ct_id, pk = value.split(':')
            ids.append((int(ct_id), int(pk)))
            data.append(score)

        # and retrieve publishables from cache
        publishables = get_cached_objects(ids, missing=SKIP)

        # create mock Listing objects to return
        return map(lambda (p, score): self._get_listing(p, score), zip(publishables, data))

    def _union(self, union_keys, pipe):
        if len(union_keys) > 1:
            result_key = '%s:zus:%s' % (self.PREFIX, md5(','.join(union_keys)).hexdigest())
            pipe.zunionstore(result_key, union_keys, 'MAX')
            pipe.expire(result_key, 60)
            return result_key
        else:
            return union_keys[0]

    def _get_base_key(self):
        key_parts = [self.PREFIX]
        # get the proper key for category
        if self.children == ListingHandler.IMMEDIATE:
            key_parts.append('c')
        elif self.children == ListingHandler.ALL:
            key_parts.append('d')
        key_parts.append(str(self.category.id))

        key = ':'.join(key_parts)
        return key


    def _get_key(self):
        pipe = None
        if not hasattr(self, '_key'):
            key = self._get_base_key()
            # do everything in one pipeline
            pipe = client.pipeline()

            # store all the key sets we will want to ZUNIONSTORE
            ct_key = None
            if self.content_types:
                # get the union of all content_type listings
                ct_key = self._union([':'.join((self.PREFIX, 'ct', str(ct.pk))) for ct in self.content_types], pipe)


            # do the intersect if required and output a single key
            if ct_key:
                inter_key = '%s:zis:%s' % (self.PREFIX, md5(','.join((ct_key, key))).hexdigest())
                pipe.zinterstore(inter_key, (ct_key, key), 'MAX')
                pipe.expire(inter_key, 60)
                key = inter_key

            if self.exclude:
                v = '%d:%d' % (self.exclude.content_type_id, self.exclude.id)

                # we are using some existing key, copy it before removing stuff
                exclude_key = '%s:exclude:%s' % (key, v)
                pipe.zunionstore(exclude_key, (key,))
                pipe.zrem(exclude_key, v)
                pipe.expire(exclude_key, 60)
                key = exclude_key

            self._key = key
        return self._key, pipe


class TimeBasedListingHandler(RedisListingHandler):
    @classmethod
    def add_publishable(cls, category, publishable, score=None, publish_from=None, pipe=None, commit=True):
        if score is None:
            score = repr(to_timestamp(publish_from or now()))
        return super(TimeBasedListingHandler, cls).add_publishable(category, publishable, score, pipe=pipe, commit=commit)

    def _get_score_limits(self):
        max_score = repr(to_timestamp(now()))
        min_score = 0

        if self.date_range:
            max_score = repr(to_timestamp(min(self.date_range[1], now())))
            min_score = repr(to_timestamp(self.date_range[0]))
        return min_score, max_score

    def _get_listing(self, publishable, score):
        Listing = get_model('core', 'listing')
        publish_from = from_timestamp(score)
        return Listing(publishable=publishable, category=publishable.category, publish_from=publish_from)


class AuthorListingHandler(TimeBasedListingHandler):
    @classmethod
    def remove_publishable(cls, publishable, pipe=None, commit=True):
        if pipe is None:
            pipe = client.pipeline()

        for k in cls.get_keys(publishable):
            pipe.zrem(k, cls.get_value(publishable))

        if commit:
            pipe.execute()
        else:
            return pipe

    @classmethod
    def add_publishable(cls, publishable, pipe=None, commit=True):
        if pipe is None:
            pipe = client.pipeline()

        for k in cls.get_keys(publishable):
            pipe.zadd(k, cls.get_value(publishable), repr(to_timestamp(publishable.publish_from)))

        if commit:
            pipe.execute()
        else:
            return pipe

    @classmethod
    def get_keys(cls, publishable):
        return [':'.join((cls.PREFIX, 'a', str(a.pk))) for a in publishable.authors.all()]

    def __init__(self, author, **kwargs):
        self.author = author
        super(AuthorListingHandler, self).__init__(None, **kwargs)

    def _get_base_key(self):
        return ':'.join((self.PREFIX, 'a', str(self.author.pk)))


class SlidingListingHandler(RedisListingHandler):
    WINDOW_SIZE = 7
    REMOVE_OLD_SLOTS = True

    @classmethod
    def base_key_set(cls):
        return ':'.join((cls.PREFIX, 'KEYS'))

    @classmethod
    def window_key_zset(cls):
        return ':'.join((cls.PREFIX, 'WINDOWS'))

    @classmethod
    def get_keys(cls, category, publishable):
        base_keys = super(SlidingListingHandler, cls).get_keys(category, publishable)
        day = date.today().strftime('%Y%m%d')
        day_mask = '%%s:%s' % day
        day_keys = [day_mask % k for k in base_keys]

        # store all the keys somewhere so that we can construct windows
        pipe = client.pipeline()
        pipe.sadd(cls.base_key_set(), *base_keys)
        pipe.zadd(cls.window_key_zset(), **dict((k, day) for k in day_keys))
        pipe.execute()

        return base_keys + day_keys

    @classmethod
    def remove_publishable(cls, category, publishable, pipe=None, commit=True):
        if pipe is None:
            pipe = client.pipeline()

        days, last_day = cls._get_days()
        base_keys = super(SlidingListingHandler, cls).get_keys(category, publishable)

        v = cls.get_value(publishable)
        for k in chain(base_keys, ('%s:%s' % (k, day) for k in base_keys for day in days)):
            pipe.zrem(k, v)

        if commit:
            pipe.execute()
        else:
            return pipe

    @classmethod
    def _get_days(cls, today=None):
        if today is None:
            today = date.today()

        days = []
        last_day = None
        for d in xrange(cls.WINDOW_SIZE):
            last_day = (today - timedelta(days=d)).strftime('%Y%m%d')
            days.append(last_day)
        return days, last_day

    @classmethod
    def regenerate(cls, today=None):
        days, last_day = cls._get_days(today)

        pipe = client.pipeline()

        if cls.REMOVE_OLD_SLOTS:
            # get all the day keys older than last day requested
            to_remove = client.zrangebyscore(cls.window_key_zset(), 0, '(' + last_day)
            if to_remove:
                # delete those keys
                pipe.delete(*to_remove)
                # and remove them from the zset index
                pipe.zremrangebyscore(cls.window_key_zset(), 0, '(' + last_day)

        for k in client.smembers(cls.base_key_set()):
            # store the aggregate for all keys over WINDOW_SIZE days
            pipe.zunionstore(k, ['%s:%s' % (k, day) for day in days], aggregate='SUM')

        pipe.execute()


def connect_signals():
    from django.db.models.signals import pre_save, post_save, post_delete, pre_delete, m2m_changed
    from ella.core.signals import content_published, content_unpublished
    from ella.core.models import Listing, Publishable

    if not core_settings.USE_REDIS_FOR_LISTINGS:
        return
    # when redis is availible, use it for authors
    m2m_changed.connect(update_authors, sender=Publishable._meta.get_field('authors').rel.through)

    content_published.connect(publishable_published)
    content_unpublished.connect(publishable_unpublished)

    pre_save.connect(listing_pre_save, sender=Listing)
    post_save.connect(listing_post_save, sender=Listing)

    pre_delete.connect(listing_pre_delete, sender=Listing)
    post_delete.connect(listing_post_delete, sender=Listing)

