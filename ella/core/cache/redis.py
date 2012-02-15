from __future__ import absolute_import

import logging
import time
from datetime import datetime

from django.conf import settings

from ella.core.cache.utils import get_cached_objects

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

REDIS_LISTING = 'listing:%d'
REDIS_CT_LISTING = 'listing:%d:%s'
CHILD_REDIS_LISTING = 'listing:%d:children'
CHILD_REDIS_CT_LISTING = 'listing:%d:children:%s'
ALL_REDIS_LISTING = 'listing:%d:all'
ALL_REDIS_CT_LISTING = 'listing:%d:all:%s'

def get_redis_values(listing):
    v = '%d:%d:%d' % (
        listing.publishable.content_type_id,
        listing.publishable_id,
        1 if listing.commercial else 0
    )
    ct_id = listing.publishable.content_type_id

    keys = []

    cat = listing.category
    keys.append(REDIS_LISTING % (cat.id))
    keys.append(REDIS_CT_LISTING % (cat.id, ct_id))

    keys.append(CHILD_REDIS_LISTING % (cat.id))
    keys.append(CHILD_REDIS_CT_LISTING % (cat.id, ct_id))

    keys.append(ALL_REDIS_LISTING % (cat.id))
    keys.append(ALL_REDIS_CT_LISTING % (cat.id, ct_id))

    if cat.tree_parent_id:
        cat = cat.get_tree_parent()
        keys.append(CHILD_REDIS_LISTING % (cat.id))
        keys.append(CHILD_REDIS_CT_LISTING % (cat.id, ct_id))

        keys.append(ALL_REDIS_LISTING % (cat.id))
        keys.append(ALL_REDIS_CT_LISTING % (cat.id, ct_id))

    while cat.tree_parent_id:
        cat = cat.get_tree_parent()
        keys.append(ALL_REDIS_LISTING % (cat.id))
        keys.append(ALL_REDIS_CT_LISTING % (cat.id, ct_id))

    return v, keys



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
    score = time.mktime(instance.publish_from.timetuple())
    for k in keys:
        pipe = pipe.zadd(k, v, score)
    pipe.execute()

def get_listing(Listing, category, children, count, offset, content_types, date_range, now):
    if content_types:
        ct_id = content_types[0].pk
        if children == Listing.objects.IMMEDIATE:
            key = CHILD_REDIS_CT_LISTING % (category.pk, ct_id)
        elif children == Listing.objects.ALL:
            key = ALL_REDIS_CT_LISTING % (category.pk, ct_id)
        else:
            key = REDIS_CT_LISTING % (category.pk, ct_id)
    elif children == Listing.objects.IMMEDIATE:
        key = CHILD_REDIS_LISTING % category.pk
    elif children == Listing.objects.ALL:
        key = ALL_REDIS_LISTING % category.pk
    else:
        key = REDIS_LISTING % category.pk

    if date_range:
        max_score = time.mktime(min(date_range[1], now).timetule())
    else:
        max_score = time.mktime(now.timetuple())

    ids = client.zrevrangebyscore(key, max_score, 0, start=offset, num=count, withscores=True)

    ids = map(lambda s: s.plit(':'), ids)

    publishables = get_cached_objects([(ct_id, pk) for (ct_id, pk, commercial) in ids])

    out = []
    for (p, tstamp), (ct_id, pk, commercial) in zip(publishables, ids):
        publish_from = datetime.fromtimestamp(tstamp)
        if date_range and publish_from < date_range[0]:
            break
        out.append(Listing(publishable=p, commercial=commercial, publish_from=publish_from))
    return out
