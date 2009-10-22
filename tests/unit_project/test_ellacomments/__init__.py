from django.contrib.sites.models import Site

from threadedcomments.models import ThreadedComment

def create_comment(obj, ct, **kwargs):
    defaults = {
        'comment': '',
        'content_type': ct,
        'object_pk': obj.pk,
        'site': Site.objects.get_current(),
    }
    defaults.update(kwargs)
    c = ThreadedComment.objects.create(**defaults)
    return c


