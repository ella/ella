import datetime

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import ObjectPaginator
from django.conf import settings

from ella.core.models import Listing, Category, HitCount
from ella.core.cache import *
from ella.core.custom_urls import dispatcher

CONTENT_TYPE_MAPPING = {}
def get_content_type(ct_name):
    """
    A helper function that returns ContentType object based on its slugified verbose_name_plural.

    Results of this function is cached to improve performance.

    Params:
        ct_name - slugified verbose_name_plural of the target model.

    Raises:
        Http404 if no matching ContentType is found
    """
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

def object_detail(request, category, year, month, day, content_type, slug, url_remainder=None):
    """
    Detail view that displays a single object based on it's main listing.

    Params:
        request - HttpRequest supplied by Django
        category - base Category tree_path (empty if home category)
        year, month, day - date matching the ``publish_from`` field of the ``Listing`` object
        content_type - slugified verbose_name_plural of the target model
        slug - slug of the object itself

    Raises:
        Http404 if object or listing doesn't exist or dates doesn't match
    """
    ct = get_content_type(content_type)

    if category:
        cat = get_cached_object_or_404(Category, tree_path=category, site__id=settings.SITE_ID)
    else:
        cat = get_cached_object_or_404(Category, tree_parent__isnull=True, site__id=settings.SITE_ID)

    obj = get_cached_object_or_404(ct, slug=slug)
    try:
        date = datetime.date(int(year), int(month), int(day))
        listing = get_cached_object_or_404(Listing, target_ct=ct, target_id=obj.id, category=cat)
        if listing.publish_from.date() != date:
            raise Http404

    except ValueError:
        # incorrect date
        raise Http404

    context = {
            'listing' : listing,
            'object' : obj,
            'category' : cat,
            'content_type_name' : content_type,
            'content_type' : ct,
}

    # check for custom actions
    if url_remainder:
        bits = url_remainder.split('/')
        return dispatcher.call_view(request, bits, context)
    elif dispatcher.has_custom_detail(obj):
        # increment hit counter
        HitCount.objects.hit(obj)
        return dispatcher.call_custom_detail(request, context)

    # increment hit counter
    HitCount.objects.hit(obj)

    return render_to_response(
            (
                # NEW
                'page/category/%s/content_type/%s.%s/%s/object.html' % (cat.path, ct.app_label, ct.model, slug),
                'page/category/%s/content_type/%s.%s/object.html' % (cat.path, ct.app_label, ct.model),
                'page/category/%s/object.html' % (cat.path),
                'page/content_type/%s.%s/object.html' % (ct.app_label, ct.model),
                'page/object.html',

                # OLD
                'category/%s/%s.%s/%s_detail.html' % (cat.path, ct.app_label, ct.model, slug),
                'category/%s/%s.%s/base_detail.html' % (cat.path, ct.app_label, ct.model),
                'category/%s/base_detail.html' % (cat.path),
                'core/object_detail.html',
),
            context,
            context_instance=RequestContext(request)
)

def list_content_type(request, category=None, year=None, month=None, day=None, content_type=None, paginate_by=20):
    """
    List object's listings according to the parameters.

    Params:
        request - HttpRequest supplied by Django
        category - base Category tree_path, optional - defaults to all categories
        year, month, day - date matching the ``publish_from`` field of the ``Listing`` object
                           All of these parameters are optional, the list will be filtered by the non-empty ones
        content_type - slugified verbose_name_plural of the target model, if omitted all content_types are listed

    Raises:
        Http404 - if the specified category or content_type does not exist or if the given date is malformed.
    """
    kwa = {}
    dates_kwa = {}
    if year:
        current_date = datetime.datetime(int(year), 1, 1)
        dates_kwa['publish_from__year'] = int(year)
        date_kind = 'month'

    if month:
        try:
            current_date = datetime.datetime(int(year), int(month), 1)
        except ValueError:
            raise Http404
        dates_kwa['publish_from__month'] = int(month)
        date_kind = 'day'

    if day:
        try:
            current_date = datetime.datetime(int(year), int(month), int(day))
        except ValueError:
            raise Http404
        dates_kwa['publish_from__day'] = int(day)
        date_kind = 'detail'

    if category:
        cat = get_cached_object_or_404(Category, tree_path=category, site__id=settings.SITE_ID)
    else:
        cat = get_cached_object_or_404(Category, tree_parent__isnull=True, site__id=settings.SITE_ID)
    kwa['category'] = cat

    if content_type:
        ct = get_content_type(content_type)
        kwa['content_types'] = [ ct ]
    else:
        ct = False

    # pagination
    if 'p' in request.GET and request.GET['p'].isdigit():
        page = int(request.GET['p'])
    else:
        page = 1

    base_qset = Listing.objects.get_queryset(**kwa)
    kwa.update(dates_kwa)
    qset = Listing.objects.get_queryset(**kwa)
    paginator = ObjectPaginator(qset.filter(**dates_kwa), paginate_by)

    if page > paginator.pages:
        raise Http404

    kwa['count'] = paginate_by
    kwa['offset'] = (page - 1) * paginate_by + 1
    listings = Listing.objects.get_listing(**kwa)

    template_list = []
    if ct:
        # NEW
        template_list.append('page/category/%s/content_type/%s.%s/listing.html' % (cat.path, ct.app_label, ct.model))
        # OLD
        template_list.append('category/%s/%s.%s/list.html' % (cat.path, ct.app_label, ct.model))
    # NEW
    template_list.append('page/category/%s/listing.html' % (cat.path))

    if ct:
        # NEW
        template_list.append('page/content_type/%s.%s/listing.html' % (ct.app_label, ct.model))

    # NEW
    template_list.append('page/listing.html')

    # OLD
    template_list.append('category/%s/base_list.html' % (cat.path))
    template_list.append('core/base_list.html')

    return render_to_response(template_list, {
            'is_paginated': paginator.pages > 1,
            'results_per_page': paginate_by,
            'has_next': paginator.has_next_page(page - 1),
            'has_previous': paginator.has_previous_page(page - 1),
            'page': page,
            'next': page + 1,
            'previous': page - 1,
            'last_on_page': paginator.last_on_page(page - 1),
            'first_on_page': paginator.first_on_page(page - 1),
            'pages': paginator.pages,
            'hits' : paginator.hits,

            'year_list' : [ (d, d.strftime(DATE_REPR["year"]), d.strftime(YEAR_URLS[date_kind])) for d in base_qset.dates('publish_from', "year", order='DESC') ],
            'date_list' : date_kind != 'detail' and [ (d, d.strftime(DATE_REPR[date_kind]), d.strftime(DATE_URLS[date_kind])) for d in qset.dates('publish_from', date_kind, order='DESC') ] or None,
            'current_date' : current_date,
            'current_date_text' : current_date.strftime(CURRENT_DATE_REPR[date_kind]),
            'date_kind' : date_kind,

            'content_type' : content_type,
            'listings' : listings,
            'category' : cat,
}, context_instance=RequestContext(request))

DATE_URLS = {'year' : '../%Y/', 'month' : '../../%Y/%m/', 'day' : '../../../%Y/%m/%d/',}
YEAR_URLS = {'year' : '../%Y/', 'month' : '../../%Y/', 'day' : '../../../%Y/', 'detail' : '../../../%Y/'}
DATE_REPR = {'year' : '%Y', 'month' : '%m/%Y', 'day' : '%d/%m/%Y', 'detail' : '%d/%m/%Y',}
CURRENT_DATE_REPR = {'year' : '', 'month' : '%Y', 'day' : '%m/%Y', 'detail' : '%d/%m/%Y',}

def home(request):
    """
    Homepage of the actual site.

    Params:
        request - HttpRequest from Django

    Raise:
        Http404 if there is no base category
    """
    cat = get_cached_object_or_404(Category, tree_parent__isnull=True, site__id=settings.SITE_ID)
    return render_to_response(
            (
                # NEW
                'page/category/%s/category.html' % (cat.slug),
                'page/category.html',

                # OLD
                'category/%s/detail.html' % (cat.slug),
                'core/category_detail.html',
),
            {
                'category' : cat,
},
            context_instance=RequestContext(request)
)

def category_detail(request, category):
    """
    Homepage of a given category.

    Params:
        request - HttpRequest from Django
        category - category's ``tree_path``

    Raise:
        Http404 if the category doesn't exist
    """
    cat = get_cached_object_or_404(Category, tree_path=category, site__id=settings.SITE_ID)
    return render_to_response(
            (
                # NEW
                'page/category/%s/category.html' % (cat.slug),
                'page/category.html',

                # OLD
                'category/%s/detail.html' % (cat.slug),
                'core/category_detail.html',
),
            {
                'category' : cat
},
            context_instance=RequestContext(request)
)

def export_test(*args, **kwargs):
    return []

def export_key(*args, **kwargs):
    return 'export:%d:%d' % (settings.SITE_ID, kwargs.get('count', 0))

@cache_this(export_key, export_test, timeout=60*60)
def export(request, count, models=None):
    if models is None:
        from ella.articles.models import Article
        models = [ Article, ]

    cat = get_cached_object_or_404(Category, tree_parent__isnull=True, site__id=settings.SITE_ID)
    listing = Listing.objects.get_listing(count=count, category=cat, mods=models)
    return render_to_response(
            ('page/export_banner.html', 'export_banner.html',),
            {'category' : cat, 'listing' : listing},
            context_instance=RequestContext(request)
)

def page_not_found(request):
    response = render_to_response('page/404.html', {}, context_instance=RequestContext(request))
    response.status_code = 404
    return response

def handle_error(request):
    response = render_to_response('page/500.html', {}, context_instance=RequestContext(request))
    response.status_code = 500
    return response
