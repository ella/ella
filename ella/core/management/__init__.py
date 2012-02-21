from datetime import datetime

from ella.core.models import Publishable
from ella.core.signals import content_published, content_unpublished

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

