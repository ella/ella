from datetime import datetime, date

from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.conf import settings
from django.template.defaultfilters import slugify
from django.db import models
from django.http import Http404
from django.shortcuts import render

from ella.core.models import Listing, Category, Placement
from ella.core.cache import get_cached_object_or_404, cache_this
from ella.core import custom_urls
from ella.core.conf import core_settings

__docformat__ = "restructuredtext en"

# local cache for get_content_type()
CONTENT_TYPE_MAPPING = {}

class EllaCoreView(object):
    ' Base class for class-based views used in ella.core.views. '

    # name of the template to be passed into get_templates
    template_name = 'TEMPLATE'

    def get_context(self, request, **kwargs):
        """
        Return a dictionary that will be then passed into the template as context.

        :Parameters:
            - `request`: current request

        :Returns:
            Dictionary with all the data
        """
        raise NotImplementedError()

    def get_templates(self, context, template_name=None):
        " Extract parameters for `get_templates` from the context. "
        if not template_name:
            template_name = self.template_name
        kw = {}
        if 'object' in context:
            o = context['object']
            kw['slug'] = o.slug

        if context.get('content_type', False):
            ct = context['content_type']
            kw['app_label'] = ct.app_label
            kw['model_label'] = ct.model

        return get_templates(template_name, category=context['category'], **kw)

    def render(self, request, context, template):
        return render(request, template, context)

    def __call__(self, request, **kwargs):
        context = self.get_context(request, **kwargs)
        return self.render(request, context, self.get_templates(context))

class ObjectDetail(EllaCoreView):
    """
    Renders a page for placement.  If ``url_remainder`` is specified, tries to
    locate custom view via :meth:`DetailDispatcher.call_view`. If
    :meth:`DetailDispatcher.has_custom_detail` returns ``True``, calls
    :meth:`DetailDispatcher.call_custom_detail`. Otherwise renders a template
    with context containing:

    * placement: ``Placement`` instance representing the URL accessed
    * object: ``Publishable`` instance bound to the ``placement``
    * category: ``Category`` of the ``placement``
    * content_type_name: slugified plural verbose name of the publishable's content type
    * content_type: ``ContentType`` of the publishable

    The template is chosen based on the object in question (the first one that matches is used):

    * ``page/category/<tree_path>/content_type/<app>.<model>/<slug>/object.html``
    * ``page/category/<tree_path>/content_type/<app>.<model>/object.html``
    * ``page/category/<tree_path>/object.html``
    * ``page/content_type/<app>.<model>/object.html``
    * ``page/object.html``

    .. note::
        The category being used in selecting a template is taken from the object's
        ``Placement``, thus one object published in many categories (even sites)
        can have a different template every time.

    :param request: ``HttpRequest`` from Django
    :param category: ``Category.tree_path`` (empty if home category)
    :param content_type: slugified ``verbose_name_plural`` of the target model
    :param year month day: date matching the `publish_from` field of the `Placement` object
    :param slug: slug of the `Placement`
    :param url_remainder: url after the object's url, used to locate custom views in `custom_urls.resolver`

    :raises Http404: if the URL is not valid and/or doesn't correspond to any valid `Placement`
    """
    template_name = 'object.html'
    def __call__(self, request, category, content_type, slug, year=None, month=None, day=None, url_remainder=None):
        context = self.get_context(request, category, content_type, slug, year, month, day)

        obj = context['object']
        # check for custom actions
        if url_remainder:
            return custom_urls.resolver.call_custom_view(request, obj, url_remainder, context)
        elif custom_urls.resolver.has_custom_detail(obj):
            return custom_urls.resolver.call_custom_detail(request, context)

        return self.render(request, context, self.get_templates(context))

    def get_context(self, request, category, content_type, slug, year, month, day):
        ct = get_content_type(content_type)

        cat = get_cached_object_or_404(Category, tree_path=category, site__id=settings.SITE_ID)

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

        # save existing object to preserve memory and SQL
        placement.category = cat
        placement.publishable.content_type = ct


        if not (placement.is_active() or request.user.is_staff):
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

def archive_year_cache_key(func, self, category):
    return 'archive_year:%d' % category.pk

class ListContentType(EllaCoreView):
    """
    List objects' listings according to the parameters. If no filtering is
    applied (including pagination), the category's title page is rendered:

    * ``page/category/<tree_path>/category.html``
    * ``page/category.html``

    Otherwise an archive template gets rendered:

    * ``page/category/<tree_path>/content_type/<app>.<model>/listing.html``
    * ``page/category/<tree_path>/listing.html``
    * ``page/content_type/<app>.<model>/listing.html``
    * ``page/listing.html``

    The context contains:

    * ``category``
    * ``listings``: list of ``Listing`` objects ordered by date and priority

    * ``page``: ``django.core.paginator.Page`` instance
    * ``is_paginated``: ``True`` if there are more pages
    * ``results_per_page``: number of objects on one page

    * ``content_type``: ``ContentType`` of the objects, if filtered on content type
    * ``content_type_name``: name of the objects' type, if filtered on content type


    :param category: ``tree_path`` of the ``Category``, root category is used if empty
    :param year, month, day: date matching the ``publish_from`` field of the ``Listing`` object.
    :param content_type: slugified verbose_name_plural of the target model, if omitted all content_types are listed
    :param page_no: which page to display
    :keyword paginate_by: number of records in one page

    All parameters are optional, filtering is done on those supplied

    :raises Http404: if the specified category or content_type does not exist or if the given date is malformed.
    """
    template_name = 'listing.html'
    title_template_name = 'category.html'

    def __call__(self, request, **kwargs):
        context = self.get_context(request, **kwargs)
        template_name = self.template_name
        if context.get('is_title_page'):
            template_name = self.title_template_name
        return self.render(request, context, self.get_templates(context, template_name))

    @cache_this(archive_year_cache_key, timeout=60*60*24)
    def _archive_entry_year(self, category):
        " Return ARCHIVE_ENTRY_YEAR from settings (if exists) or year of the newest object in category "
        year = getattr(settings, 'ARCHIVE_ENTRY_YEAR', None)
        if not year:
            now = datetime.now()
            try:
                year = Listing.objects.filter(
                        category__site__id=settings.SITE_ID,
                        category__tree_path__startswith=category.tree_path,
                        publish_from__lte=now
                    ).values('publish_from')[0]['publish_from'].year
            except:
                year = now.year
        return year

    def get_context(self, request, category='', year=None, month=None, \
        day=None, content_type=None, paginate_by=core_settings.CATEGORY_LISTINGS_PAGINATE_BY):
        # pagination
        if 'p' in request.GET and request.GET['p'].isdigit():
            page_no = int(request.GET['p'])
        else:
            page_no = 1

        # if we are not on the first page, display a different template
        category_title_page = page_no == 1

        kwa = {}
        if year:
            category_title_page = False
            year = int(year)
            kwa['publish_from__year'] = year

        if month:
            try:
                month = int(month)
                date(year, month, 1)
            except ValueError, e:
                raise Http404()
            kwa['publish_from__month'] = month

        if day:
            try:
                day = int(day)
                date(year, month, day)
            except ValueError, e:
                raise Http404()
            kwa['publish_from__day'] = day

        cat = get_cached_object_or_404(Category, tree_path=category, site__id=settings.SITE_ID)
        kwa['category'] = cat
        if category:
            kwa['children'] = Listing.objects.ALL

        if content_type:
            ct = get_content_type(content_type)
            kwa['content_types'] = [ ct ]
        else:
            ct = False

        qset = Listing.objects.get_queryset_wrapper(kwa)
        paginator = Paginator(qset, paginate_by)

        if page_no > paginator.num_pages or page_no < 1:
            raise Http404()

        page = paginator.page(page_no)
        listings = page.object_list

        context = {
                'page': page,
                'is_paginated': paginator.num_pages > 1,
                'results_per_page': paginate_by,

                'content_type' : ct,
                'content_type_name' : content_type,
                'listings' : listings,
                'category' : cat,
                'is_homepage': not bool(category) and page_no == 1 and year is None,
                'is_title_page': category_title_page,
                'archive_entry_year' : lambda: self._archive_entry_year(cat),
            }

        return context

# backwards compatibility
object_detail = ObjectDetail()
home = category_detail = list_content_type = ListContentType()

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
        app_label = placement.publishable.content_type.app_label
    if model_label is None:
        model_label = placement.publishable.content_type.model
    return get_templates(name, slug, category, app_label, model_label)


def get_export_key(func, request, count, name='', content_type=None):
    return 'ella.core.views.export:%d:%d:%s:%s' % (
            settings.SITE_ID, count, name, content_type
        )

@cache_this(get_export_key, timeout=core_settings.CACHE_TIMEOUT_LONG)
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

    cat = get_cached_object_or_404(Category, tree_path='', site__id=settings.SITE_ID)
    listing = Listing.objects.get_listing(count=count, category=cat)
    return render(
            request,
            t_list,
            { 'category' : cat, 'listing' : listing },
            content_type=content_type
        )


##
# Error handlers
##
def page_not_found(request):
    response = render(request, 'page/404.html', {})
    response.status_code = 404
    return response

def handle_error(request):
    response = render(request, 'page/500.html', {})
    response.status_code = 500
    return response
