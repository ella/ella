from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.template import RequestContext
from django.core.paginator import ObjectPaginator
from django.conf import settings
from django.template.defaultfilters import slugify
from django.db import models
from django.http import Http404

from ella.core.models import Listing, Category, HitCount, Placement
from ella.core.cache import get_cached_list, get_cached_object_or_404, cache_this
from ella.core.custom_urls import dispatcher
from ella.core.cache.template_loader import render_to_response


# local cache for get_content_type()
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
        for model in models.get_models():
            if ct_name == slugify(model._meta.verbose_name_plural):
                ct = ContentType.objects.get_for_model(model)
                CONTENT_TYPE_MAPPING[ct_name] = ct
                break
        else:
            raise Http404
    return ct

def object_detail(request, category, content_type, slug, year=None, month=None, day=None, url_remainder=None):
    """
    Detail view that displays a single object based on it's main placement.

    Params:
        request - HttpRequest supplied by Django
        category - base Category tree_path (empty if home category)
        year, month, day - date matching the ``publish_from`` field of the ``Placement`` object
        content_type - slugified verbose_name_plural of the target model
        slug - slug of the object itself

    Raises:
        Http404 if object or placement doesn't exist or dates doesn't match
    """
    ct = get_content_type(content_type)

    if category:
        cat = get_cached_object_or_404(Category, tree_path=category, site__id=settings.SITE_ID)
    else:
        cat = get_cached_object_or_404(Category, tree_parent__isnull=True, site__id=settings.SITE_ID)

    if year:
        placement = get_cached_object_or_404(Placement,
                    publish_from__year=year,
                    publish_from__month=month,
                    publish_from__day=day,
                    target_ct=ct,
                    category=cat,
                    slug=slug,
                    static=False
)
    else:
        placement = get_cached_object_or_404(Placement, category=cat, target_ct=ct, slug=slug, static=True)

    if not (placement.is_active() or request.user.is_staff):
        # future placement, render if accessed by logged in staff member
        raise Http404

    obj = placement.target

    context = {
            'placement' : placement,
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
        HitCount.objects.hit(placement)
        return dispatcher.call_custom_detail(request, context)

    # increment hit counter
    HitCount.objects.hit(placement)

    return render_to_response(
        get_templates('object.html', slug, cat, ct.app_label, ct.model),
        context,
        context_instance=RequestContext(request)
)

def get_templates(name, slug=None, category=None, app_label=None, model_label=None):
    """
    Returns templates in following format and order:
        'page/category/%s/content_type/%s.%s/%s/%s' % (category.path, app_label, model_label, slug, name),
        'page/category/%s/content_type/%s.%s/%s' % (category.path, app_label, model_label, name),
        'page/category/%s/%s' % (category.path, name),
        'page/content_type/%s.%s/%s' % (app_label, model_label, name),
        'page/%s' % name,

    TODO: Allow Placement() as parameter?
    """
    templates = []
    if category:
        if app_label and model_label:
            if slug:
                templates.append('page/category/%s/content_type/%s.%s/%s/%s' % (category.path, app_label, model_label, slug, name))
            templates.append('page/category/%s/content_type/%s.%s/%s' % (category.path, app_label, model_label, name))
        templates.append('page/category/%s/%s' % (category.path, name))
    if app_label and model_label:
        templates.append('page/content_type/%s.%s/%s' % (app_label, model_label, name))
    templates.append('page/%s' % name)
    return templates

def get_templates_from_placement(name, placement, slug=None, category=None, app_label=None, model_label=None):
    """ Returns template list by placement. """
    if slug is None:
        slug = placement.slug
    if category is None:
        category = placement.category
    if app_label is None:
        app_label = placement.target._meta.app_label
    if model_label is None:
        model_label = placement.target._meta.module_name
    return get_templates(name, slug, category, app_label, model_label)

def list_content_type(request, category=None, year=None, month=None, day=None, content_type=None, paginate_by=20):
    """
    List objects' listings according to the parameters.

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
        current_date = datetime(int(year), 1, 1)
        dates_kwa['publish_from__year'] = int(year)
        date_kind = 'month'

    if month:
        try:
            current_date = datetime(int(year), int(month), 1)
        except ValueError:
            raise Http404
        dates_kwa['publish_from__month'] = int(month)
        date_kind = 'day'

    if day:
        try:
            current_date = datetime(int(year), int(month), int(day))
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
        template_list.append('page/category/%s/content_type/%s.%s/listing.html' % (cat.path, ct.app_label, ct.model))
    template_list.append('page/category/%s/listing.html' % (cat.path))

    if ct:
        template_list.append('page/content_type/%s.%s/listing.html' % (ct.app_label, ct.model))

    template_list.append('page/listing.html')


    url_prepend = ''
    url_apend = ''
    if ct:
        url_prepend = '../'
        url_apend = content_type + '/'

    # list of years with published objects
    year_list = [
            (d, d.strftime(DATE_REPR["year"]), url_prepend + d.strftime(YEAR_URLS[date_kind]))
            for d in base_qset.dates('publish_from', "year", order='DESC')
        ]

    # list of dates with published objects
    date_list = None
    if date_kind != 'detail':
        date_list = [
                (d, d.strftime(DATE_REPR[date_kind]), url_prepend + d.strftime(DATE_URLS[date_kind]) + url_apend)
                for d in qset.dates('publish_from', date_kind, order='DESC')
            ]

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

            'year_list' : year_list,
            'date_list' : date_list,
            'current_date' : current_date,
            'current_date_text' : current_date.strftime(CURRENT_DATE_REPR[date_kind]),
            'date_kind' : date_kind,

            'content_type' : content_type,
            'listings' : listings,
            'category' : cat,
}, context_instance=RequestContext(request))

# format lookups for year_list and date_list
DATE_URLS = {'month' : '../%Y/%m/', 'day' : '../../%Y/%m/%d/',}
YEAR_URLS = {'month' : '../%Y/', 'day' : '../../%Y/', 'detail' : '../../../%Y/',}
DATE_REPR = {'year' : '%Y', 'month' : '%m/%Y', 'day' : '%d/%m/%Y', 'detail' : '%d/%m/%Y',}
CURRENT_DATE_REPR = {'month' : '%Y', 'day' : '%m/%Y', 'detail' : '%d/%m/%Y',}

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
                'page/category/%s/category.html' % (cat.path),
                'page/category.html',
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
                'page/category/%s/category.html' % (cat.path),
                'page/category.html',
),
            {
                'category' : cat
},
            context_instance=RequestContext(request)
)

def get_export_key(func, request, count, name='', content_type=None):
    return 'ella.core.views.export:%d:%d:%s:%s' % (
            settings.SITE_ID, count, name, content_type
)

@cache_this(get_export_key, timeout=60*60)
def export(request, count, name='', content_type=None):
    """
    Export banners.

    Params:
        count - number of objects to pass into the template
        name - name of the template (page/export/banner.html is default)
        models - list of Model classes to include
    """
    t_list = []
    if name:
        t_list.append('page/export/%s.html' % name)
    t_list.append('page/export/banner.html')

    cat = get_cached_object_or_404(Category, tree_parent__isnull=True, site__id=settings.SITE_ID)
    listing = Listing.objects.get_listing(count=count, category=cat)
    return render_to_response(
            t_list,
            {'category' : cat, 'listing' : listing},
            context_instance=RequestContext(request),
            content_type=content_type
)


##
# Error handlers
##
def page_not_found(request):
    response = render_to_response('page/404.html', {}, context_instance=RequestContext(request))
    response.status_code = 404
    return response

def handle_error(request):
    response = render_to_response('page/500.html', {}, context_instance=RequestContext(request))
    response.status_code = 500
    return response
