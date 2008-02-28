from django.conf import settings

from ella.media.queue.dummy import DummyQueue


__all__ = (
    'QUEUE',
)


QUEUE = DummyQueue()

ACTIVE_MQ_HOST = getattr(settings, 'ACTIVE_MQ_HOST', None)
if ACTIVE_MQ_HOST:
    raise NotImplemented('working with ACTIVE_MQ_HOST not implemted yet...')

