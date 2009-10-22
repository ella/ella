from django.contrib.sites.models import Site

from threadedcomments.models import ThreadedComment

def create_comment(obj, ct):
        c = ThreadedComment.objects.create(
            comment='',
            content_type=ct,
            object_pk=obj.pk,
            site=Site.objects.get_current(),
        )
        return c


