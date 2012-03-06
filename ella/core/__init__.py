from django.utils.translation import ugettext_lazy as _
trans_app_label = _('Core')

# add some of our templatetags to builtins
from ella.core import templatetags

from ella.core.cache import redis

if redis.client:
    from django.db.models.signals import pre_save, post_save, post_delete
    from django.dispatch import receiver
    from ella.core.signals import content_published, content_unpublished
    from ella.core.models import Listing
    receiver(content_published)(redis.publishable_published)
    receiver(content_unpublished)(redis.publishable_unpublished)
    receiver(pre_save, sender=Listing)(redis.listing_pre_save)
    receiver(post_save, sender=Listing)(redis.listing_post_save)
    receiver(post_delete, sender=Listing)(redis.listing_post_delete)
