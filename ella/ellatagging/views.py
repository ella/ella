"""
Tagging related views.
"""
import urllib
from datetime import datetime

from django.template import RequestContext, Context
from django.template.defaultfilters import slugify
from django.shortcuts import render_to_response
from django.db import connection
from django.shortcuts import get_object_or_404

from tagging.models import Tag, TaggedItem

from ella.core.models import Placement
from ella.core.models import Publishable

def get_tagged_publishables(tag):
    return TaggedItem.objects.get_by_model(
        Publishable.objects.filter(placement__publish_from__lt=datetime.now()), 
        tag)

def tagged_publishables(request, tag):
    tag = get_object_or_404(Tag, name=tag)
    object_list = get_tagged_publishables(tag)
    context = Context({
        'tag': tag,
        'object_list': object_list,
    })
    return render_to_response(
        [
            'page/tagging/%s/listing.html' % slugify(tag),
            'page/tagging/listing.html',
        ],
        context,
        context_instance=RequestContext(request))
