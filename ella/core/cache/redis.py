from __future__ import absolute_import

import logging
import time
from datetime import datetime
from hashlib import md5

from django.conf import settings
from django.db.models.loading import get_model

from ella.core.cache.utils import get_cached_objects
from ella.core.managers import ListingHandler

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

def publishable_published(publishable, **kwargs):
    pipe = client.pipeline()
    for l in publishable.listing_set.all():
        RedisListingHandler.add_publishable(
            l.category,
            publishable,
            repr(time.mktime(l.publish_from.timetuple())),
            pipe=pipe,
            commit=False
        )
    pipe.execute()

def publishable_unpublished(publishable, **kwargs):
    pipe = client.pipeline()
    for l in publishable.listing_set.all():
        RedisListingHandler.remove_publishable(
            l.category,
            publishable,
            pipe=pipe,
            commit=False
        )
    pipe.execute()

def listing_pre_delete(sender, instance, **kwargs):
    # prepare redis pipe for deletion...
    instance.__pipe = RedisListingHandler.remove_publishable(
        instance.category,
        instance.publishable,
        commit=False
    )

def listing_post_delete(sender, instance, **kwargs):
    # but only delete it if the model delete went through
    pipe = instance.__pipe
    for l in instance.publishable.listing_set.all():
        RedisListingHandler.add_publishable(
            l.category,
            instance.publishable,
            repr(time.mktime(l.publish_from.timetuple())),
            pipe=pipe,
            commit=False
        )
    pipe.execute()

def listing_pre_save(sender, instance, **kwargs):
    if instance.pk:
        # prepare deletion of stale data
        old_listing = instance.__class__.objects.get(pk=instance.pk)
        instance.__pipe = RedisListingHandler.remove_publishable(
            instance.category,
            old_listing.publishable,
            commit=False
        )

def listing_post_save(sender, instance, **kwargs):
    pipe = getattr(instance, '__pipe', None)
    if instance.publishable.is_published():
        pipe = RedisListingHandler.add_publishable(
            instance.category,
            instance.publishable,
            repr(time.mktime(instance.publish_from.timetuple())),
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

        # children
        keys.append(':'.join((cls.PREFIX, 'c', str(category.id))))
        if category.tree_parent_id:
            keys.append(':'.join((cls.PREFIX, 'c', str(category.tree_parent_id))))

        # all children
        keys.append(':'.join((cls.PREFIX, 'd', str(category.id))))
        while category.tree_parent_id:
            category = category.tree_parent
            keys.append(':'.join((cls.PREFIX, 'd', str(category.id))))

        # content_type
        keys.append(':'.join((cls.PREFIX, 'ct', str(publishable.content_type_id))))

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
    def remove_publishable(cls, category, publishable, pipe=None, commit=False):
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
        return Listing(publishable=publishable, category=publishable.category, publish_from=datetime.fromtimestamp(score))

    def _get_score_limits(self):
        max_score = None
        min_score = None

        if self.date_range:
            max_score = time.mktime(min(self.date_range[1], datetime.now()).timetule())
            min_score = time.mktime(self.date_range[0].timetuple())
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
                start=offset, num=offset+count-1,
                withscores=True
            )
        else:
            pipe = pipe.zrevrange(key,
                start=offset, num=offset+count-1,
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
        publishables = get_cached_objects(ids)

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
                pipe.zunionstore(exclude_key, (key, ))
                pipe.zrem(exclude_key, v)
                pipe.expire(exclude_key, 60)
                key = exclude_key

            self._key = key
        return self._key, pipe

def connect_signals():
    from django.db.models.signals import pre_save, post_save, post_delete, pre_delete
    from ella.core.signals import content_published, content_unpublished
    from ella.core.models import Listing
    content_published.connect(publishable_published)
    content_unpublished.connect(publishable_unpublished)

    pre_save.connect(listing_pre_save, sender=Listing)
    post_save.connect(listing_post_save, sender=Listing)

    pre_delete.connect(listing_pre_delete, sender=Listing)
    post_delete.connect(listing_post_delete, sender=Listing)

if client:
    connect_signals()
