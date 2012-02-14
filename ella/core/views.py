from datetime import datetime, date

from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.conf import settings
from django.db import models
from django.http import Http404
from django.shortcuts import redirect
from django.template.defaultfilters import slugify
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _

from ella.core.models import Listing, Category, Publishable
from ella.core.cache import get_cached_object_or_404, cache_this
from ella.core import custom_urls
from ella.core.conf import core_settings
from ella.core.cache.utils import get_cached_object

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
        return TemplateResponse(request, template, context)

    def __call__(self, request, **kwargs):
        context = self.get_context(request, **kwargs)
        return self.render(request, context, self.get_templates(context))

class ObjectDetail(EllaCoreView):
    """
    Renders a page for publishable.  If ``url_remainder`` is specified, tries to
    locate custom view via :meth:`DetailDispatcher.call_view`. If
    :meth:`DetailDispatcher.has_custom_detail` returns ``True``, calls
    :meth:`DetailDispatcher.call_custom_detail`. Otherwise renders a template
    with context containing:

    * object: ``Publishable`` instance representing the URL accessed
    * category: ``Category`` of the ``object``
    * content_type_name: slugified plural verbose name of the publishable's content type
    * content_type: ``ContentType`` of the publishable

    The template is chosen based on the object in question (the first one that matches is used):

    * ``page/category/<tree_path>/content_type/<app>.<model>/<slug>/object.html``
    * ``page/category/<tree_path>/content_type/<app>.<model>/object.html``
    * ``page/category/<tree_path>/object.html``
    * ``page/content_type/<app>.<model>/object.html``
    * ``page/object.html``

    :param request: ``HttpRequest`` from Django
    :param category: ``Category.tree_path`` (empty if home category)
    :param content_type: slugified ``verbose_name_plural`` of the target model
    :param year month day: date matching the `publish_from` field of the `Publishable` object
    :param slug: slug of the `Publishable`
    :param url_remainder: url after the object's url, used to locate custom views in `custom_urls.resolver`

    :raises Http404: if the URL is not valid and/or doesn't correspond to any valid `Publishable`
    """
    template_name = 'object.html'
    def __call__(self, request, category, content_type, slug, year=None, month=None, day=None, id=None, url_remainder=None):
        context = self.get_context(request, category, content_type, slug, year, month, day, id)

        obj = context['object']

        if obj.static and slug != obj.slug:
            return redirect(obj.get_absolute_url(), permanent=True)

        # check for custom actions
        if url_remainder:
            return custom_urls.resolver.call_custom_view(request, obj, url_remainder, context)
        elif custom_urls.resolver.has_custom_detail(obj):
            return custom_urls.resolver.call_custom_detail(request, context)

        return self.render(request, context, self.get_templates(context))

    def get_context(self, request, category, content_type, slug, year, month, day, id):
        ct = get_content_type(content_type)

        cat = get_cached_object_or_404(Category, timeout=3600, tree_path=category, site__id=settings.SITE_ID)

        if year:
            publishable = get_cached_object_or_404(Publishable,
                        publish_from__year=year,
                        publish_from__month=month,
                        publish_from__day=day,
                        content_type=ct,
                        category=cat,
                        slug=slug,
                        static=False
                    )
        else:
            publishable = get_cached_object_or_404(Publishable, pk=id)
            if publishable.category_id != cat.pk or publishable.content_type_id != ct.id or not publishable.static:
                raise Http404()

        # save existing object to preserve memory and SQL
        publishable.category = cat
        publishable.content_type = ct


        if not (publishable.is_published() or request.user.is_staff):
            # future publish, render if accessed by logged in staff member
            raise Http404

        obj = publishable.target

        context = {
                'object' : obj,
                'category' : cat,
                'content_type_name' : content_type,
                'content_type' : ct,
            }

        return context

def archive_year_cache_key(self, category):
    return 'core.archive_year:%d' % category.pk

class ListContentType(EllaCoreView):
    """
    List objects' listings according to the parameters. If no filtering is
    applied (including pagination), the category's title page is rendered. The
    template used depends on ``template`` attribute for category being rendered.
    Default template is ``category.html``, so it would look like this:

    * ``page/category/<tree_path>/category.html``
    * ``page/category.html``
    
    If custom template is selected, let's say ``static_page.html``, it would
    result in:
    
    * ``page/category/<tree_path>/static_page.html``
    * ``page/static_page.html``

    If filtering is active, an archive template gets rendered:

    * ``page/category/<tree_path>/content_type/<app>.<model>/listing.html``
    * ``page/category/<tree_path>/listing.html``
    * ``page/content_type/<app>.<model>/listing.html``
    * ``page/listing.html``

    The context contains:

    * ``category``
    * ``listings``: list of ``Listing`` objects ordered by date

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
    empty_homepage_template_name = 'debug/empty_homepage.html'

    class EmptyHomepageException(Exception): pass

    def __call__(self, request, **kwargs):
        try:
            context = self.get_context(request, **kwargs)
            template_name = self.template_name
            if context.get('is_title_page'):
                template_name = context['category'].template
            return self.render(request, context, self.get_templates(context, template_name))
        except self.EmptyHomepageException:
            return self.render(request, {}, self.empty_homepage_template_name)

    def _handle_404(self, explanation, is_homepage):
        if settings.DEBUG is True and is_homepage:
            raise self.EmptyHomepageException()
        raise Http404(explanation)

    @cache_this(archive_year_cache_key, timeout=60 * 60 * 24)
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

        # Homepage is considered when category is empty (~ no slug) and no
        # filtering is used.
        # 
        # Homepage behaves differently on 404 with DEBUG mode to let user 
        # know everything is fine instead of 404. Also, indication of 
        # homepage is added to context, it's usually good to know, if your
        # on homepage, right? :)
        #
        # @see: _handle_404()
        is_homepage = not bool(category) and page_no == 1 and year is None

        if month:
            try:
                month = int(month)
                date(year, month, 1)
            except ValueError:
                return self._handle_404(_('Invalid month value %r') % month,
                    is_homepage)
            kwa['publish_from__month'] = month

        if day:
            try:
                day = int(day)
                date(year, month, day)
            except ValueError:
                return self._handle_404(_('Invalid day value %r') % day,
                    is_homepage)
            kwa['publish_from__day'] = day

        try:
            cat = get_cached_object(Category, timeout=3600, tree_path=category,
                site__id=settings.SITE_ID)
        except Category.DoesNotExist:
            return self._handle_404(_('Category with tree path %(path)r does not '
                'exist on site %(site)s') %
                    {'path': category, 'site': settings.SITE_ID}, is_homepage)

        kwa['category'] = cat
        if category:
            kwa['children'] = Listing.objects.ALL

        if content_type:
            ct = get_content_type(content_type)
            kwa['content_types'] = (ct,)
        else:
            ct = False

        qset = Listing.objects.get_queryset_wrapper(kwa)
        paginator = Paginator(qset, paginate_by)

        if page_no > paginator.num_pages or page_no < 1:
            return self._handle_404(_('Invalid page number %r') % page_no,
                is_homepage)

        page = paginator.page(page_no)
        listings = page.object_list

        context = {
            'category' : cat,
            'is_homepage': is_homepage,
            'is_title_page': category_title_page,
            'is_paginated': paginator.num_pages > 1,
            'results_per_page': paginate_by,
            'page': page,
            'listings' : listings,
            'archive_entry_year' : lambda: self._archive_entry_year(cat),

            'content_type' : ct,
            'content_type_name' : content_type,
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

    * ``'page/category/%s/content_type/%s.%s/%s/%s' % (<CATEGORY_PART>, app_label, model_label, slug, name)``
    * ``'page/category/%s/content_type/%s.%s/%s' % (<CATEGORY_PART>, app_label, model_label, name)``
    * ``'page/category/%s/%s' % (<CATEGORY_PART>, name)``
    * ``'page/content_type/%s.%s/%s' % (app_label, model_label, name)``
    * ``'page/%s' % name``
    
    Where ``<CATEGORY_PART>`` is derived from ``path`` attribute by these rules:
    
    * When **no** parent exists (this is therfore root category) ``<CATEGORY_PART> = path``
    * When exactly **one** parent exists: ``<CATEGORY_PART> = path``
    * When multiple parent exist (category nestedN is deep in the tree)::
          
          <CATEGORY_PART> = (
              'nested1/nested2/../nestedN/',
              'nested1/nested2/../nestedN-1/',
              ...
              'nested1'
          )
       
    Examples. Three categories exist having slugs **ROOT**, **NESTED1**,
    **NESTED2** where **NESTED2**'s parent is **NESTED1**.::
    
        ROOT
           \
         NESTED1
             \
            NESTED2 
    
    * For **ROOT**, ``<CATEGORY_PART>`` is only one - "ROOT".
    * For **NESTED1**, ``<CATEGORY_PART>`` is only one - "NESTED1".
    * For **NESTED2**, ``<CATEGORY_PART>`` has two elements: "NESTED1/NESTED2" and "NESTED1".
    """
    def category_templates(category, incomplete_template, params):
        paths = []
        parts = category.path.split('/')
        for i in reversed(range(1, len(parts) + 1)):
            params.update({'pth': '/'.join(parts[:i])})
            paths.append(incomplete_template % params)
        return paths

    FULL = 'page/category/%(pth)s/content_type/%(app_label)s.%(model_label)s/%(slug)s/%(name)s'
    FULL_NO_SLUG = 'page/category/%(pth)s/content_type/%(app_label)s.%(model_label)s/%(name)s'
    BY_CATEGORY = 'page/category/%(pth)s/%(name)s'
    BY_CONTENT_TYPE = 'page/content_type/%(app_label)s.%(model_label)s/%(name)s'

    templates = []
    params = {'name': name}

    if app_label and model_label:
        params.update({'app_label': app_label, 'model_label': model_label})

    if slug:
        params.update({'slug': slug})

    if category:
        if app_label and model_label:
            if slug:
                templates += category_templates(category, FULL, params)
            templates += category_templates(category, FULL_NO_SLUG, params)
        templates += category_templates(category, BY_CATEGORY, params)

    if app_label and model_label:
        templates.append(BY_CONTENT_TYPE % params)

    templates.append('page/%(name)s' % params)
    return templates


def get_templates_from_publishable(name, publishable):
    """
    Returns the same template list as `get_templates` but gets values from `Publishable` instance.
    """
    slug = publishable.slug
    category = publishable.category
    app_label = publishable.content_type.app_label
    model_label = publishable.content_type.model
    return get_templates(name, slug, category, app_label, model_label)


def get_export_key(request, count, name='', content_type=None):
    return 'core.export:%d:%d:%s:%s' % (
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

    cat = get_cached_object_or_404(Category, timeout=3600, tree_path='', site__id=settings.SITE_ID)
    listing = Listing.objects.get_listing(count=count, category=cat)
    return TemplateResponse(
            request,
            t_list,
            { 'category' : cat, 'listing' : listing },
            content_type=content_type
        )


##
# Error handlers
##
def page_not_found(request):
    response = TemplateResponse(request, 'page/404.html', {})
    response.status_code = 404
    return response

def handle_error(request):
    response = TemplateResponse(request, 'page/500.html', {})
    response.status_code = 500
    return response
