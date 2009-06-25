"""
Tagging related views.
"""
from datetime import datetime

from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from tagging.models import Tag, TaggedItem

from ella.core.models import Publishable

def get_tagged_publishables(tag):
    now = datetime.now()
    queryset = Publishable.objects.filter(
            Q(placement__publish_to__isnull=True) | Q(placement__publish_to__gt=now),
            placement__publish_from__lt=now
        ) .distinct()
    return TaggedItem.objects.get_by_model(queryset, tag)

def tagged_publishables(request, tag):
    tag = get_object_or_404(Tag, name=tag)
    object_list = get_tagged_publishables(tag)
    context = {
        'tag': tag,
        'object_list': object_list,
    }
    return render_to_response(
        [
            'page/tagging/%s/listing.html' % slugify(tag),
            'page/tagging/listing.html',
        ],
        context,
        context_instance=RequestContext(request))
