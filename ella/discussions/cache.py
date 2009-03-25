"""
Module contains cached filtered QuerySets from
ella.discussions.models.get_comments_on_thread .
Cache-key functions included.
"""

from ella.core.cache.utils import cache_this

from ella.discussions.models import get_comments_on_thread


def get_key_comments_on_thread__by_submit_date(func, thread):
    return 'ella.discussions.cache.comments_on_thread__by_submit_date:%d' % thread.pk

@cache_this(get_key_comments_on_thread__by_submit_date)
def comments_on_thread__by_submit_date(thread):
    out = get_comments_on_thread(thread).order_by('submit_date')
    return list(out)

def get_key_comments_on_thread__spec_filter(func, thread):
    return 'ella.discussions.cache.comments_on_thread__spec_filter:%d' % thread.pk

@cache_this(get_key_comments_on_thread__spec_filter)
def comments_on_thread__spec_filter(thread):
    out = get_comments_on_thread(thread).filter(is_public__exact=True).order_by('submit_date')
    return list(out)
