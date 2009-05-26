"""
Tagging related views.
"""
from datetime import datetime

from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db import connection

from tagging.models import Tag, TaggedItem

from ella.core.models import Publishable


qn = connection.ops.quote_name

def get_tagged_publishables(tag):
    now = datetime.now()
    model_opts = Publishable._meta
    publishable_table = qn(model_opts.db_table)
    queryset = Publishable.objects.filter(
            Q(placement__publish_to__isnull=True) | Q(placement__publish_to__gt=now),
            placement__publish_from__lt=now
        ) 

    opts = TaggedItem._meta
    tagged_item_table = qn(opts.db_table)
    return queryset.extra(
        tables=[opts.db_table],
        where=[
            '%s.content_type_id = %s.%s' % (tagged_item_table, publishable_table, qn(model_opts.get_field('content_type').column)),
            '%s.tag_id = %%s' % tagged_item_table,
            '%s.%s = %s.object_id' % (publishable_table,
                                        qn(model_opts.pk.column),
                                        tagged_item_table)
        ],  
        params=[tag.pk],
    )

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
