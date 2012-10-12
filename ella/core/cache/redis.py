from __future__ import absolute_import

import logging
from datetime import date, timedelta
from hashlib import md5

from django.conf import settings
from django.db.models.loading import get_model

from ella.core.cache.utils import get_cached_objects, SKIP
from ella.core.managers import ListingHandler
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


DEFAULT_REDIS_HANDLER = 'redis'

def ListingHandlerClass():
    return get_model('core', 'Listing').objects.get_listing_handler(DEFAULT_REDIS_HANDLER)


def publishable_published(publishable, **kwargs):
    pipe = client.pipeline()
    for l in publishable.listing_set.all():
        ListingHandlerClass().add_publishable(
            l.category,
            publishable,
            repr(to_timestamp(l.publish_from)),
            pipe=pipe,
            commit=False
        )
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

    for l in instance.publishable.listing_set.all():
        ListingHandlerClass().add_publishable(
            l.category,
            instance.publishable,
            repr(to_timestamp(l.publish_from)),
            pipe=pipe,
            commit=False
        )
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
    pipe = getattr(instance, '__pipe', None)

    if instance.publishable.is_published():
        pipe = ListingHandlerClass().add_publishable(
            instance.category,
            instance.publishable,
            repr(to_timestamp(instance.publish_from)),
            pipe=pipe,
            commit=False
        )
    if pipe:
        pipe.execute()


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
        publish_from = from_timestamp(score)
        return Listing(publishable=publishable, category=publishable.category, publish_from=publish_from)

    def _get_score_limits(self):
        max_score = None
        min_score = None

        if self.date_range:
            max_score = repr(to_timestamp(min(self.date_range[1], now())))
            min_score = repr(to_timestamp(self.date_range[0]))
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
                repr(max_score), repr(min_score),
                start=offset, num=offset + count - 1,
                withscores=True
            )
        else:
            pipe = pipe.zrevrange(key,
                start=offset, num=offset + count - 1,
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

    def _get_key(self):
        pipe = None
        if not hasattr(self, '_key'):
            key_parts = [self.PREFIX]
            # get the proper key for category
            if self.children == ListingHandler.IMMEDIATE:
                key_parts.append('c')
            elif self.children == ListingHandler.ALL:
                key_parts.append('d')
            key_parts.append(str(self.category.id))

            key = ':'.join(key_parts)

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


class AuthorListingHandler(RedisListingHandler):
    @classmethod
    def get_keys(cls, category, publishable):
        keys = super(AuthorListingHandler, cls).get_keys(category, publishable)

        # Add keys for all the authors.
        for a in publishable.authors.all():
            keys.append(':'.join((cls.PREFIX, 'a', str(a.pk))))

        return keys

    def _get_key(self):
        key, pipe = super(AuthorListingHandler, self)._get_key()

        if pipe is not None and 'author' in self.kwargs:
            # If author filtering is requested, perform another intersect
            # over what has been filtered out before.
            a_key = '%s:a:%s' % (self.PREFIX, self.kwargs['author'].pk)
            a_inter_key = '%s:azis:%s' % (self.PREFIX, md5(','.join((a_key, key))).hexdigest())
            pipe.zinterstore(a_inter_key, (a_key, key), 'MAX')
            pipe.expire(a_inter_key, 60)
            self._key = a_inter_key

        return self._key, pipe


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
    def regenerate(cls, today=None):
        if today is None:
            today = date.today()

        days = []
        last_day = None
        for d in xrange(cls.WINDOW_SIZE):
            last_day = (today - timedelta(days=d)).strftime('%Y%m%d')
            days.append(last_day)

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
    if not client:
        return
    LH = ListingHandlerClass()
    if LH is None or not hasattr(LH, 'add_publishable') or not hasattr(LH, 'remove_publishable'):
        return
    from django.db.models.signals import pre_save, post_save, post_delete, pre_delete
    from ella.core.signals import content_published, content_unpublished
    from ella.core.models import Listing
    content_published.connect(publishable_published)
    content_unpublished.connect(publishable_unpublished)

    pre_save.connect(listing_pre_save, sender=Listing)
    post_save.connect(listing_post_save, sender=Listing)

    pre_delete.connect(listing_pre_delete, sender=Listing)
    post_delete.connect(listing_post_delete, sender=Listing)

