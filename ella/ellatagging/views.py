"""
Tagging related views.
"""
import urllib

from django.template import RequestContext, Context
from django.template.defaultfilters import slugify
from django.shortcuts import render_to_response
from django.db import connection

from tagging.models import Tag, TaggedItem

from ella.core.models import Placement
from ella.core.models import Publishable


#@cache_this TODO
def _get_tagged_placements(tag_name):
    """ returns placements """
    tags = Tag.objects.filter(name=tag_name)
    qn = connection.ops.quote_name
    if not tags:
        return []
    tag = tags[0]
    sql = """
        SELECT
            p.id
        FROM
            %(tab_tagged_item)s AS t,
            %(tab_placement)s AS p
        WHERE
            p.target_id = t.object_id
            AND
            p.target_ct_id = t.content_type_id
            AND
            t.tag_id = %(tag_id)d
            AND
            p.publish_from <= NOW()
        GROUP BY
            p.id
        ORDER BY
            p.publish_from, p.publish_to
    """ % {
        'tag_id': tag.pk,
        'tab_tagged_item': qn(TaggedItem._meta.db_table),
        'tab_placement': qn(Placement._meta.db_table),}
    cursor = connection.cursor()
    cursor.execute(sql)
    placements = map(lambda row: Placement.objects.get(pk=row[0]), cursor.fetchall())
    return placements

def tagged_publishables(request, tag):
    """ return tagged Publishable objects (i.e. Articles, Galleries,...) """
    things = []
    for p in _get_tagged_placements(tag):
        t = p.target
        if isinstance(t, Publishable):
            things.append(t)
    cx = Context({
        'objects': things,
        'paginate_by': 10,
        'tag': tag,
        'extra_context': {'tag': tag},
        'object_list': things,})
    return render_to_response(
        [
            'page/tagging/%s/listing.html' % slugify(tag),
            'page/tagging/listing.html',
            #'page/tagging/view_publishables.html',
        ],
        cx,
        context_instance=RequestContext(request))
