from ella.core.signals import content_published, content_unpublished
from ella.core.models import Publishable, Listing
from ella.utils import timezone


def regenerate_publish_signals(now=None):
    if now is None:
        now = timezone.now()

    qset = Publishable.objects.filter(publish_from__lt=now, published=True).exclude(publish_to__lt=now)
    for p in qset:
        content_published.send(sender=p.content_type.model_class(), publishable=p)


def generate_publish_signals(now=None):
    if now is None:
        now = timezone.now()

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


def regenerate_listing_handlers(today=None):
    if today is None:
        today = timezone.now().date()

    Listing.objects.get_listing_handler('default')
    for lh in Listing.objects._listing_handlers.values():
        lh.regenerate(today)
