from datetime import datetime

from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from ella.core.models import Publishable, Listing
from ella.core.signals import content_published, content_unpublished
from ella.core.cache import redis

if redis.client:
    receiver(pre_save, sender=Listing)(redis.listing_pre_save)
    receiver(post_save, sender=Listing)(redis.listing_post_save)
    receiver(post_delete, sender=Listing)(redis.listing_post_delete)

def generate_publish_signals(now=None):
    if now is None:
        now = datetime.now()

    # content that went live and isn't announced yet
    qset = Publishable.objects.filter(announced=False, publish_from__lt=now, published=True).exclude(publish_to__lt=now)
    for p in qset:
        content_published.send(sender=p.content_type.model_class(), publishable=p)
    qset.update(announced=True)

    # content that went down but was announced as live
    qset = Publishable.objects.filter(announced=True, publish_to__lt=now, published=True)
    for p in qset:
        content_unpublished.send(sender=p.content_type.model_class(), publishable=p)
    qset.update(announced=False)

