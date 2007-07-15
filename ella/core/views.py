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
    try:
        date = datetime.date(int(year), int(month), int(day))
    except ValueError:
        raise Http404

    cat = get_cached_object_or_404(CATEGORY_CT, tree_path=category)
    obj = get_cached_object_or_404(ct, slug=slug)
    try:
        listing = get_cached_object(LISTING_CT, target_ct=ct, target_id=obj.id, category=cat)
    except Listing.DoesNotExist:
        listing = None
        if Listing.objects.filter(target_ct=ct, target_id=obj.id):
            raise Http404

    return render_to_response(
            (
                'category/%s/%s/%s_detail.html' % (cat.tree_path, content_type, slug),
                'category/%s/%s/base_detail.html' % (cat.tree_path, content_type),
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
            kwa['publish_from'] = datetime.date(int(year), int(month), int(day))
        except ValueError:
            raise Http404
    elif month:
        kwa['publish_from__month'] = month
    elif year:
        kwa['publish_from__year'] = year

    if category:
        kwa['category'] = get_cached_object_or_404(CATEGORY_CT, slug=category)

    if content_type:
        kwa['content_types'] = get_content_type(content_type)
        cat = get_cached_object_or_404(CATEGORY_CT, tree_path=category)
    else:
        cat = False

    # TODO: pagination
    listings = Listing.objects.get_listing(**kwa)

    template_list = []
    if cat and content_type:
        template_list.append('category/%s/%s/list.html' % (cat.tree_path, content_type))
    if content_type:
        template_list.append('core/content_type/%s/list.html' % content_type)
    if cat:
        template_list.append('category/%s/base_list.html' % cat.tree_path)
    template_list.append('core/list.html')

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
    cat = get_cached_object_or_404(CATEGORY_CT, tree_path=category)
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
