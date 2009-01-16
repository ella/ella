"""
Tagging related views.
"""
import urllib

from django.http import Http404, HttpResponse
from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_list
from django.template import RequestContext, loader, Context
from django.template.defaultfilters import slugify
from django.shortcuts import render_to_response
from ella.tagging.fields import SuggestTagField
from django.db import connection
from django import forms

from ella.tagging.models import Tag, TaggedItem
from ella.tagging.utils import get_tag, get_queryset_and_model
from ella.core.models import Placement
from ella.db.models import Publishable

def tagged_object_list(request, queryset_or_model=None, tag=None,
        related_tags=False, related_tag_counts=True, **kwargs):
    """
    A thin wrapper around
    ``django.views.generic.list_detail.object_list`` which creates a
    ``QuerySet`` containing instances of the given queryset or model
    tagged with the given tag.

    In addition to the context variables set up by ``object_list``, a
    ``tag`` context variable will contain the ``Tag`` instance for the
    tag.

    If ``related_tags`` is ``True``, a ``related_tags`` context variable
    will contain tags related to the given tag for the given model.
    Additionally, if ``related_tag_counts`` is ``True``, each related
    tag will have a ``count`` attribute indicating the number of items
    which have it in addition to the given tag.
    """
    if queryset_or_model is None:
        try:
            queryset_or_model = kwargs.pop('queryset_or_model')
        except KeyError:
            raise AttributeError(_('tagged_object_list must be called with a queryset or a model.'))

    if tag is None:
        try:
            tag = kwargs.pop('tag')
        except KeyError:
            raise AttributeError(_('tagged_object_list must be called with a tag.'))

    tag_instance = get_tag(tag)
    if tag_instance is None:
        raise Http404(_('No Tag found matching "%s".') % tag)
    queryset = TaggedItem.objects.get_by_model(queryset_or_model, tag_instance)
    if not kwargs.has_key('extra_context'):
        kwargs['extra_context'] = {}
    kwargs['extra_context']['tag'] = tag_instance
    if related_tags:
        kwargs['extra_context']['related_tags'] = \
            Tag.objects.related_for_model(tag_instance, queryset_or_model,
                                          counts=related_tag_counts)
    return object_list(request, queryset, **kwargs)

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
        'tab_placement': qn(Placement._meta.db_table),
}
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
        'object_list': things,
})
    return render_to_response(
        [
            'page/tagging/%s/listing.html' % slugify(tag),
            'page/tagging/listing.html',
            #'page/tagging/view_publishables.html',
        ],
        cx,
        context_instance=RequestContext(request)
)

# --- suggest

def tags_json_view(request, **kwargs):
    tag_begin = ''
    if 'q' in request.GET:
        tag_begin = request.GET.get('q')
    elif 'tag' in kwargs:
        tag_begin = kwargs['tag']
    start = tag_begin.strip()
    ft = []
    if len(start) > 0:
        data = Tag.objects.filter(name__startswith=start.lower())
        for item in data:
            ft.append(item.__unicode__().encode('utf-8'))
    res = HttpResponse('\n'.join(ft), mimetype='text/html;charset=utf-8')
    return res

class TagForm(forms.Form):
    tags = SuggestTagField()

def tag_form_view(request, **kwargs):
    if 'tags' in request:
        f = TagForm({'tags':request['tags']})
    else:
        f = TagForm()
    return render_to_response(
        'tag_form.html',
        {'form': f,}
)

