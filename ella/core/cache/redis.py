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
    pipe = instance.__redis_pipe
    v, keys = get_redis_values(instance)
    score = repr(time.mktime(instance.publish_from.timetuple()))
    for k in keys:
        pipe = pipe.zadd(k, v, score)
    pipe.execute()


class RedisListingHandler(ListingHandler):
    def count(self):
        key, pipe = self._get_key()
        if pipe is None:
            pipe = client.pipeline()
        pipe = pipe.zcard(key)
        results = pipe.execute()
        return results[-1]

    def get_listings(self, offset=0, count=10):
        Listing = get_model('core', 'listing')
        key, pipe = self._get_key()

        # get the score range based on the date range
        if self.date_range:
            max_score = time.mktime(min(self.date_range[1], datetime.now()).timetule())
            min_score = time.mktime(self.date_range[0].timetuple())
        else:
            max_score = time.time()
            min_score = 0

        # get all the relevant records
        if pipe is None:
            pipe = client.pipeline()
        pipe = pipe.zrevrangebyscore(key,
            repr(max_score), repr(min_score),
            start=offset, num=count,
            withscores=True, score_cast_func=lambda s: datetime.fromtimestamp(float(s))
        )
        results = pipe.execute()

        # get the data from redis into proper format
        ids = map(lambda (s, ts): s.split(':') + [ts], results[-1])
        # and retrieve publishables from cache
        publishables = get_cached_objects([(ct_id, pk) for (ct_id, pk, commercial, ts) in ids])

        # create mock Listing objects to return
        out = []
        for p, (ct_id, pk, commercial, tstamp) in zip(publishables, ids):
            out.append(Listing(publishable=p, commercial=commercial, publish_from=tstamp))
        return out

    def _union(self, unions, pipe):
        inter_keys = []
        for union_keys in unions:
            if len(union_keys) > 1:
                result_key = 'listings:zus:' + md5(','.join(union_keys)).hexdigest()
                pipe.zunionstore(result_key, union_keys)
                inter_keys.append(result_key)
            else:
                inter_keys.append(union_keys[0])
        return inter_keys

    def _get_key(self):
        pipe = None
        if not hasattr(self, '_key'):
            Listing = get_model('core', 'listing')
            # store all the key sets we will want to ZUNIONSTORE
            unions = []
            if self.content_types:
                # get the union of all content_type listings
                ct_keys = [REDIS_CT_LISTING % ct.pk for ct in self.content_types]
                unions.append(ct_keys)

            # get the union of all category listings
            cat_keys = [REDIS_CAT_LISTING % self.category.id]
            if self.children == Listing.objects.IMMEDIATE:
                cat_keys.extend(REDIS_CAT_LISTING % c.id for c in self.category.get_children())
            elif self.children == Listing.objects.ALL:
                cat_keys.extend(REDIS_CAT_LISTING % c.id for c in self.category.get_children(True))
            unions.append(cat_keys)

            # do everything in one pipeline
            pipe = client.pipeline()

            # do all the unions if required and output a list of keys to intersect
            inter_keys = self._union(unions, pipe)

            # do the intersect if required and output a single key
            if len(inter_keys) > 1:
                key = 'listings:zis:' + md5(','.join(inter_keys)).hexdigest()
                pipe.zinterstore(key, inter_keys)
            else:
                key = inter_keys[0]

            self._key = key
        return self._key, pipe

