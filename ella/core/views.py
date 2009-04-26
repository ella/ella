from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.template import RequestContext
from django.core.paginator import QuerySetPaginator
from django.conf import settings
from django.template.defaultfilters import slugify
from django.db import models
from django.http import Http404

from ella.core.models import Listing, Category, Placement
from ella.core.cache import get_cached_object_or_404, cache_this
from ella.core.custom_urls import dispatcher
from ella.core.cache.template_loader import render_to_response

__docformat__ = "restructuredtext en"

# local cache for get_content_type()
CONTENT_TYPE_MAPPING = {}
CACHE_TIMEOUT_LONG = getattr(settings, 'CACHE_TIMEOUT_LONG', 60 * 60)

def get_content_type(ct_name):
    """
    A helper function that returns ContentType object based on its slugified verbose_name_plural.

    Results of this function is cached to improve performance.

    :Parameters: 
        - `ct_name`:  Slugified verbose_name_plural of the target model.

    :Exceptions: 
        - `Http404`: if no matching ContentType is found
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
    Renders a page for placement. All the data fetching and context creation is done in `_object_detail`.
    If `url_remainder` is specified, tries to locate custom view via `dispatcher`. Renders a template 
    returned by `get_template` with context returned by `_object_detail`.

    :Parameters:
        - `request`: `HttpRequest` from Django
        - `category, content_type, slug, year, month, day`: parameters passed on to `_object_detail`
        - `url_remainder`: url after the object's url, used to locate custom views in `dispatcher`

    :Exceptions: 
        - `Http404`: if the URL is not valid and/or doesn't correspond to any valid `Placement`
    """
    context = _object_detail(request.user, category, content_type, slug, year, month, day)

    obj = context['object']
    # check for custom actions
    if url_remainder:
        bits = url_remainder.split('/')
        return dispatcher.call_view(request, bits, context)
    elif dispatcher.has_custom_detail(obj):
        return dispatcher.call_custom_detail(request, context)

    return render_to_response(
        get_templates('object.html', slug, context['category'], context['content_type'].app_label, context['content_type'].model),
        context,
        context_instance=RequestContext(request)
    )

def category_detail(request, category):
    context = _category_detail(category)
    return render_to_response(
            (
            'page/category/%s/category.html' % (context["category"].path),
            'page/category.html',
            ),
            context,
            context_instance=RequestContext(request)
        )

def list_content_type(request, category=None, year=None, month=None, day=None, content_type=None, paginate_by=20):
    # pagination
    if 'p' in request.GET and request.GET['p'].isdigit():
        page_no = int(request.GET['p'])
    else:
        page_no = 1

    context = _list_content_type(category, year, month, day, content_type, page_no, paginate_by)
    if content_type:
        ct = get_content_type(content_type)
    else:
        ct = False
    template_list = []
    if ct:
        template_list.append('page/category/%s/content_type/%s.%s/listing.html' % (context["cat"].path, ct.app_label, ct.model))
    template_list.append('page/category/%s/listing.html' % (context["cat"].path))
    if ct:
        template_list.append('page/content_type/%s.%s/listing.html' % (ct.app_label, ct.model))
    template_list.append('page/listing.html')
    return render_to_response(
            template_list,
            context,
            context_instance=RequestContext(request)
        )

def home(request):
    """
    Homepage of the actual site.

    :Parameters: 
        - `request`: `HttpRequest` from Django

    :Exceptions: 
        - `Http404`: if there is no base category
    """
    context = _category_detail()
    return render_to_response(
            (
            'page/category/%s/category.html' % (context['category'].path),
            'page/category.html',
            ),
            context,
            context_instance=RequestContext(request)
        )

def _object_detail(user, category, content_type, slug, year=None, month=None, day=None):
    """
    Helper function that does all the data fetching for `object_detail` view. It
    returns a dictionary containing:

        - `placement`: `Placement` instance representing the URL accessed
        - `object`: `Publishable` instance bound to the `placement`
        - `category`: `Category` of the `placement`
        - `content_type_name`: slugified plural verbose name of the publishable's content type
        - `content_type`: `ContentType` of the publishable

    :Parameters: 
        - `user`: django `User` instance
        - `category`: `Category.tree_path` (empty if home category)
        - `year`, `month`, `day`: date matching the `publish_from` field of the `Placement` object
        - `content_type`: slugified `verbose_name_plural` of the target model
        - `slug`: slug of the `Placement`

    :Exceptions:
        - `Http404`: if object or placement doesn't exist or dates don't match
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
                    publishable__content_type=ct,
                    category=cat,
                    slug=slug,
                    static=False
                )
    else:
        placement = get_cached_object_or_404(Placement, category=cat, publishable__content_type=ct, slug=slug, static=True)

    if not (placement.is_active() or user.is_staff):
        # future placement, render if accessed by logged in staff member
        raise Http404

    obj = placement.publishable.target

    context = {
            'placement' : placement,
            'object' : obj,
            'category' : cat,
            'content_type_name' : content_type,
            'content_type' : ct,
        }

    return context


def get_templates(name, slug=None, category=None, app_label=None, model_label=None):
    """
    Returns templates in following format and order:

        - 'page/category/%s/content_type/%s.%s/%s/%s' % ( category.path, app_label, model_label, slug, name ),
        - 'page/category/%s/content_type/%s.%s/%s' % ( category.path, app_label, model_label, name ),
        - 'page/category/%s/%s' % ( category.path, name ),
        - 'page/content_type/%s.%s/%s' % ( app_label, model_label, name ),
        - 'page/%s' % name,
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
    """
    Returns the same template list as `get_templates` but generates the missing values from `Placement` instance.
    """
    if slug is None:
        slug = placement.slug
    if category is None:
        category = placement.category
    if app_label is None:
        app_label = placement.publishable.target._meta.app_label
    if model_label is None:
        model_label = placement.publishable.target._meta.module_name
    return get_templates(name, slug, category, app_label, model_label)

def _list_content_type(category, year, month=None, day=None, content_type=None, page_no=1, paginate_by=20):
    """
    List objects' listings according to the parameters.

    :Parameters:
        - `category`: base Category tree_path, optional - defaults to all categories
        - `year, month, day`: date matching the `publish_from` field of the `Placement` object.
          All of these parameters are optional, the list will be filtered by the non-empty ones
        - `content_type`: slugified verbose_name_plural of the target model, if omitted all content_types are listed
        - `page_no`: which page to display
        - `paginate_by`: number of records in one page

    :Exceptions:
        - `Http404`: if the specified category or content_type does not exist or if the given date is malformed.
    """
    kwa = {}
    dates_kwa = {}
    current_date = datetime(int(year), 1, 1)
    dates_kwa['publish_from__year'] = int(year)
    date_kind = 'month'

    if month:
        try:
            current_date = datetime(int(year), int(month), 1)
        except ValueError:
            raise Http404()
        dates_kwa['publish_from__month'] = int(month)
        date_kind = 'day'

    if day:
        try:
            current_date = datetime(int(year), int(month), int(day))
        except ValueError:
            raise Http404()
        dates_kwa['publish_from__day'] = int(day)
        date_kind = 'detail'

    if category:
        cat = get_cached_object_or_404(Category, tree_path=category, site__id=settings.SITE_ID)
        kwa['category__tree_path__startswith'] = category
    else:
        cat = get_cached_object_or_404(Category, tree_parent__isnull=True, site__id=settings.SITE_ID)
        kwa['category'] = cat

    if content_type:
        ct = get_content_type(content_type)
        kwa['content_types'] = [ ct ]
    else:
        ct = False

    base_qset = Listing.objects.get_queryset(**kwa)
    kwa.update(dates_kwa)
    # FIXME: FAIL, this ignores priorities
    qset = Listing.objects.get_queryset(**kwa)
    paginator = QuerySetPaginator(qset.filter(**dates_kwa), paginate_by)

    if page_no > paginator.num_pages or page_no < 1:
        raise Http404()

    kwa['count'] = paginate_by
    kwa['offset'] = (page_no - 1) * paginate_by + 1
    page = paginator.page(page_no)
    listings = page.object_list

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

    context = {
            'page': page,
            'is_paginated': paginator.num_pages > 1,
            'results_per_page': paginate_by,

            'year_list' : year_list,
            'date_list' : date_list,
            'current_date' : current_date,
            'current_date_text' : current_date.strftime(CURRENT_DATE_REPR[date_kind]),
            'date_kind' : date_kind,

            'content_type' : content_type,
            'listings' : listings,
            'category' : cat,
        }

    return context

# format lookups for year_list and date_list
DATE_URLS = { 'month' : '../%Y/%m/', 'day' : '../../%Y/%m/%d/', }
YEAR_URLS = { 'month' : '../%Y/', 'day' : '../../%Y/', 'detail' : '../../../%Y/', }
DATE_REPR = { 'year' : '%Y', 'month' : '%m/%Y', 'day' : '%d/%m/%Y', 'detail' : '%d/%m/%Y', }
CURRENT_DATE_REPR = { 'month' : '%Y', 'day' : '%m/%Y', 'detail' : '%d/%m/%Y', }

def __archive_entry_year(category):
    " Return ARCHIVE_ENTRY_YEAR from settings (if exists) or year of the newest object in category "
    year = getattr(settings, 'ARCHIVE_ENTRY_YEAR', None)
    if not year:
        now = datetime.now()
        try:
            categories = Category.objects.filter(site__id=settings.SITE_ID, tree_path__startswith=category.tree_path)
            year = Listing.objects.filter(category__in=categories, publish_from__lte=now)[0].publish_from.year
        except:
            year = now.year
    return year

def _category_detail(tree_path=False):
    """
    Helper function that does all the data fetching for `home` and `category_detail` views. Returns
    a dictionary containing:

        - `category`: the root `Category` of the site
        - `is_homepage`: boolean whether the category is the root category
        - `archive_entry_year`: year of last `Listing`

    :Parameters: 
        - `tree_path`: `Category.tree_path` (empty if home category)

    :Exceptions: 
        - `Http404`: if there is no base category
    """
    if tree_path:
        cat = get_cached_object_or_404(Category, tree_path=tree_path, site__id=settings.SITE_ID)
    else:
        cat = get_cached_object_or_404(Category, tree_parent__isnull=True, site__id=settings.SITE_ID)
    context = {
                'category' : cat,
                'is_homepage': not bool(tree_path),
                'archive_entry_year' : __archive_entry_year(cat),
            }

    return context


def get_export_key(func, request, count, name='', content_type=None):
    return 'ella.core.views.export:%d:%d:%s:%s' % (
            settings.SITE_ID, count, name, content_type
        )

@cache_this(get_export_key, timeout=CACHE_TIMEOUT_LONG)
def export(request, count, name='', content_type=None):
    """
    Export banners.

    :Parameters:
        - `count`: number of objects to pass into the template
        - `name`: name of the template ( page/export/banner.html is default )
        - `models`: list of Model classes to include
    """
    t_list = []
    if name:
        t_list.append('page/export/%s.html' % name)
    t_list.append('page/export/banner.html')

    cat = get_cached_object_or_404(Category, tree_parent__isnull=True, site__id=settings.SITE_ID)
    listing = Listing.objects.get_listing(count=count, category=cat)
    return render_to_response(
            t_list,
            { 'category' : cat, 'listing' : listing },
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
