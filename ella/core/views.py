import datetime

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response
from django.template import RequestContext

from ella.core.models import Listing, Category
from ella.core.cache import *

CONTENT_TYPE_MAPPING = {}
def get_content_type(ct_name):
    try:
        ct = CONTENT_TYPE_MAPPING[ct_name]
    except KeyError:
        from django.db import models
        from django.template.defaultfilters import slugify
        for model in models.get_models():
            if ct_name == slugify(model._meta.verbose_name_plural):
                ct = ContentType.objects.get_for_model(model)
                CONTENT_TYPE_MAPPING[ct_name] = ct
                break
        else:
            raise Http404
    return ct

LISTING_CT = ContentType.objects.get_for_model(Listing)
CATEGORY_CT = ContentType.objects.get_for_model(Category)

def object_detail(request, category, year, month, day, content_type, slug):
    ct = get_content_type(content_type)

    cat = get_cached_object_or_404(CATEGORY_CT, tree_path=category)
    obj = get_cached_object_or_404(ct, slug=slug)
    try:
        date = datetime.date(int(year), int(month), int(day))
        listing = get_cached_object_or_404(LISTING_CT, target_ct=ct, target_id=obj.id, category=cat)
        if listing.publish_from.date() != date:
            raise Http404

    except ValueError:
        # incorrect date
        raise Http404

    return render_to_response(
            (
                'category/%s/%s.%s/%s_detail.html' % (cat.tree_path, ct.app_label, ct.model, slug),
                'category/%s/%s.%s/base_detail.html' % (cat.tree_path, ct.app_label, ct.model),
                'category/%s/base_detail.html' % (cat.tree_path),
                'core/object_detail.html',
),
            {
                'listing' : listing,
                'object' : obj
},
            context_instance=RequestContext(request)
)

def list_content_type(request, category=None, year=None, month=None, day=None, content_type=None):
    kwa = {}
    if day and month and year:
        try:
            datetime.date(int(year), int(month), int(day))
        except ValueError:
            raise Http404
    if day:
        kwa['publish_from__day'] = int(day)
    if month:
        month = int(month)
        if month > 12:
            raise Http404
        kwa['publish_from__month'] = month
    if year:
        kwa['publish_from__year'] = year

    if category:
        cat = get_cached_object_or_404(CATEGORY_CT, tree_path=category)
        kwa['category'] = cat
    else:
        cat = False

    if content_type:
        ct = get_content_type(content_type)
        kwa['content_types'] = [ ct ]
    else:
        ct = False

    # TODO: pagination
    listings = Listing.objects.get_listing(**kwa)

    template_list = []
    if cat and ct:
        template_list.append('category/%s/%s.%s/list.html' % (cat.tree_path, ct.app_label, ct.model))
    if cat:
        template_list.append('category/%s/base_list.html' % cat.tree_path)
    template_list.append('core/base_list.html')

    return render_to_response(template_list, {'listings' : listings}, context_instance=RequestContext(request))

def home(request):
    cat = get_cached_object_or_404(CATEGORY_CT, tree_parent__isnull=True)
    return render_to_response(
            (
                'category/%s/detail.html' % (cat.tree_path),
                'core/category_detail.html',
),
            {
                'category' : cat
},
            context_instance=RequestContext(request)
)

def category_detail(request, category):
    cat = get_cached_object_or_404(CATEGORY_CT, tree_path=category, tree_parent__isnull=False)
    return render_to_response(
            (
                'category/%s/detail.html' % (cat.tree_path),
                'core/category_detail.html',
),
            {
                'category' : cat
},
            context_instance=RequestContext(request)
)
