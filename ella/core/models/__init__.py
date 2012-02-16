from ella.core.models.main import *
from ella.core.models.publishable import *

from ella.core.cache import redis
if redis.client:
    from django.db.models.signals import pre_save, post_save, post_delete
    from django.dispatch import receiver
    receiver(pre_save, sender=Listing)(redis.listing_pre_save)
    receiver(post_save, sender=Listing)(redis.listing_post_save)
    receiver(post_delete, sender=Listing)(redis.listing_post_delete)
del redis
