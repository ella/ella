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
            publishable,
            repr(time.mktime(l.publish_from.timetuple())),
            ['1' if l.commercial else '0'],
            pipe=pipe,
            commit=False
        )
    pipe.execute()

def publishable_unpublished(publishable, **kwargs):
    pipe = client.pipeline()
    for l in publishable.listing_set.all():
        RedisListingHandler.remove_publishable(publishable, ['1' if l.commercial else '0'], pipe=pipe, commit=False)
    pipe.execute()

def listing_pre_delete(sender, instance, **kwargs):
    # prepare redis pipe for deletion...
    instance.__pipe = RedisListingHandler.remove_publishable(instance.publishable, ['1' if instance.commercial else '0'], commit=False)

def listing_post_delete(sender, instance, **kwargs):
    # but only delete it if the model delete went through
    instance.__pipe.execute()

def listing_pre_save(sender, instance, **kwargs):
    if instance.pk:
        # prepare deletion of stale data
        old_listing = instance.__class__.objects.get(pk=instance.pk)
        instance.__pipe = RedisListingHandler.remove_publishable(old_listing.publishable, ['1' if old_listing.commercial else '0'], commit=False)

def listing_post_save(sender, instance, **kwargs):
    RedisListingHandler.add_publishable(
        instance.publishable,
        repr(time.mktime(instance.publish_from.timetuple())),
        ['1' if instance.commercial else '0'],
        pipe=getattr(instance, '__pipe', None)
    )

class RedisListingHandler(ListingHandler):
    PREFIX = 'listing'

    @classmethod
    def get_value(cls, publishable, data):
        return ':'.join([str(publishable.content_type_id), str(publishable.pk)] + data)

    @classmethod
    def get_keys(cls, publishable):
        cat = publishable.category
        # main cat
        keys = [':'.join((cls.PREFIX, str(cat.id)))]

        # children
        keys.append(':'.join((cls.PREFIX, 'c', str(cat.id))))
        if cat.tree_parent_id:
            keys.append(':'.join((cls.PREFIX, 'c', str(cat.tree_parent_id))))

        # all children
        keys.append(':'.join((cls.PREFIX, 'd', str(cat.id))))
        while cat.tree_parent_id:
            cat = cat.tree_parent
            keys.append(':'.join((cls.PREFIX, 'd', str(cat.id))))

        # content_type
        keys.append(':'.join((cls.PREFIX, 'ct', str(publishable.content_type_id))))

        return keys

    @classmethod
    def add_publishable(cls, publishable, score, data=[], pipe=None, commit=True):
        if pipe is None:
            pipe = client.pipeline()

        for k in cls.get_keys(publishable):
            pipe.zadd(k, cls.get_value(publishable, data), score)

        if commit:
            pipe.execute()
        else:
            return pipe

    @classmethod
    def remove_publishable(cls, publishable, data=[], pipe=None, commit=False):
        if pipe is None:
            pipe = client.pipeline()

        for k in cls.get_keys(publishable):
            pipe.zrem(k, cls.get_value(publishable, data))

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

    def _get_listing(self, publishable, score, data):
        Listing = get_model('core', 'listing')
        return Listing(publishable=publishable, category=publishable.category, commercial=data[0], publish_from=datetime.fromtimestamp(score))

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
                start=offset, num=offset+count,
                withscores=True
            )
        else:
            pipe = pipe.zrevrange(key,
                start=offset, num=offset+count,
                withscores=True
            )
        results = pipe.execute()

        # get the data from redis into proper format
        data = []
        ids = []
        for value, score in results[-1]:
            value = value.split(':')
            ids.append((int(value[0]), int(value[1])))
            data.append((score, value[2:]))

        # and retrieve publishables from cache
        publishables = get_cached_objects(ids)

        # create mock Listing objects to return
        return map(lambda (p, (score, d)): self._get_listing(p, score, d), zip(publishables, data))

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
                ct_key = self._union([':'.join(self.PREFIX, 'ct', str(ct.pk)) for ct in self.content_types], pipe)


            # do the intersect if required and output a single key
            if ct_key:
                inter_key = '%s:zis:%s' % (self.PREFIX, md5(','.join((ct_key, key))).hexdigest())
                pipe.zinterstore(inter_key, (ct_key, key), 'MAX')
                pipe.expire(inter_key, 60)
                key = inter_key

            if self.exclude:
                v = '%d:%d:' % (self.exclude.content_type_id, self.exclude.id)
                v1, v2 = v + '0', v + '1'

                # we are using some existing key, copy it before removing stuff
                exclude_key = '%s:exclude:%s' % (key, v)
                pipe.zunionstore(exclude_key, (key, ))
                pipe.zrem(exclude_key, v1, v2)
                pipe.expire(exclude_key, 60)
                key = exclude_key

            self._key = key
        return self._key, pipe

