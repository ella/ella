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

REDIS_CAT_LISTING = 'listing:cat:%d'
REDIS_CT_LISTING = 'listing:ct:%d'

def get_redis_values(listing):
    v = '%d:%d:%d' % (
        listing.publishable.content_type_id,
        listing.publishable_id,
        1 if listing.commercial else 0
    )
    return v, (
        REDIS_CAT_LISTING % (listing.category_id),
        REDIS_CT_LISTING % (listing.publishable.content_type_id)
    )

def publishable_published(publishable, **kwargs):
    for l in publishable.listing_set.all():
        listing_post_save(l.__class__, l)

def publishable_unpublished(publishable, **kwargs):
    for l in publishable.listing_set.all():
        listing_post_delete(l.__class__, l)


def listing_post_delete(sender, instance, **kwargs):
    pipe = client.pipeline()
    v, keys = get_redis_values(instance)
    for k in keys:
        for k in keys:
            pipe = pipe.zrem(k, v)
    pipe.execute()

def listing_pre_save(sender, instance, **kwargs):
    pipe = client.pipeline()
    if instance.pk:
        old_listing = instance.__class__.objects.get(pk=instance.pk)
        v, keys = get_redis_values(old_listing)
        for k in keys:
            pipe = pipe.zrem(k, v)

    instance.__redis_pipe = pipe


def listing_post_save(sender, instance, **kwargs):
    if hasattr(instance, '__redis_pipe'):
        pipe = instance.__redis_pipe
    else:
        pipe = client.pipeline()
    v, keys = get_redis_values(instance)
    score = repr(time.mktime(instance.publish_from.timetuple()))
    for k in keys:
        pipe = pipe.zadd(k, v, score)
    pipe.execute()


class RedisListingHandler(ListingHandler):
    CT_LISTING = REDIS_CT_LISTING
    CAT_LISTING = REDIS_CAT_LISTING

    def count(self):
        key, pipe = self._get_key()
        if pipe is None:
            pipe = client.pipeline()
        pipe = pipe.zcard(key)
        results = pipe.execute()
        return results[-1]

    def _get_listing(self, publishable, score, data):
        Listing = get_model('core', 'listing')
        return Listing(publishable=publishable, commercial=data[0], publish_from=datetime.fromtimestamp(score))

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
                start=offset, num=count,
                withscores=True
            )
        else:
            pipe = pipe.zrevrange(key,
                start=offset, num=count,
                withscores=True
            )
        results = pipe.execute()

        # get the data from redis into proper format
        data = []
        ids = []
        for value, score in results[-1]:
            value = value.split(':')
            ids.append((value[0], value[1]))
            data.append((score, value[2:]))

        # and retrieve publishables from cache
        publishables = get_cached_objects(ids)

        # create mock Listing objects to return
        return map(lambda (p, (score, d)): self._get_listing(p, score, d), zip(publishables, data))

    def _union(self, unions, pipe):
        inter_keys = []
        for union_keys in unions:
            if len(union_keys) > 1:
                result_key = 'listings:zus:' + md5(','.join(union_keys)).hexdigest()
                pipe.zunionstore(result_key, union_keys, 'MAX')
                inter_keys.append(result_key)
            else:
                inter_keys.append(union_keys[0])
        return inter_keys

    def _get_key(self):
        pipe = None
        if not hasattr(self, '_key'):
            # store all the key sets we will want to ZUNIONSTORE
            unions = []
            if self.content_types:
                # get the union of all content_type listings
                ct_keys = [self.CT_LISTING % ct.pk for ct in self.content_types]
                unions.append(ct_keys)

            # get the union of all category listings
            cat_keys = [self.CAT_LISTING % self.category.id]
            if self.children == ListingHandler.IMMEDIATE:
                cat_keys.extend(self.CAT_LISTING % c.id for c in self.category.get_children())
            elif self.children == ListingHandler.ALL:
                cat_keys.extend(self.CAT_LISTING % c.id for c in self.category.get_children(True))
            unions.append(cat_keys)

            # do everything in one pipeline
            pipe = client.pipeline()

            # do all the unions if required and output a list of keys to intersect
            inter_keys = self._union(unions, pipe)

            # do the intersect if required and output a single key
            if len(inter_keys) > 1:
                key = 'listings:zis:' + md5(','.join(inter_keys)).hexdigest()
                pipe.zinterstore(key, inter_keys, 'MAX')
            else:
                key = inter_keys[0]

            if self.exclude:
                v = '%d:%d:' % (self.exclude.content_type_id, self.exclude.id)
                v1, v2 = v + '0', v + '1'

                # we are using some existing key, copy it before removing stuff
                exclude_key = '%s:exclude:%s' % (key, v)
                pipe.zunionstore(exclude_key, (key, ))
                pipe.zrem(exclude_key, v1, v2)
                key = exclude_key

            self._key = key
        return self._key, pipe

