from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.http import Http404
from django.shortcuts import redirect, render
from django.template.defaultfilters import slugify
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.views.generic.list import ListView

from ella.core.models import Listing, Category, Publishable, Author
from ella.core.cache import get_cached_object_or_404, cache_this, get_cached_object
from ella.core import custom_urls
from ella.core.conf import core_settings
from ella.core.signals import object_rendering, object_rendered
from ella.api import render_as_api
from ella.utils.timezone import now, localize

__docformat__ = "restructuredtext en"

# local cache for get_content_type()
CONTENT_TYPE_MAPPING = {}


class AuthorView(ListView):
    model = Publishable
    context_object_name = 'listings'
    allow_empty = True
    paginate_by = core_settings.CATEGORY_LISTINGS_PAGINATE_BY
    template_name = 'page/author.html'

    def get(self, request, *args, **kwargs):
        if 'slug' not in kwargs:
            raise Http404

        # Compatibility with `paginator` tag.
        if 'p' in request.GET:
            self.kwargs.update({'page': request.GET['p']})

        self.author = get_cached_object_or_404(Author, slug=kwargs['slug'])

        response = render_as_api(request, self.author)
        if response:
            return response

        return super(AuthorView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return self.author.recently_published()

    def get_context_data(self, **kwargs):
        base = super(AuthorView, self).get_context_data(**kwargs)
        base.update({'object': self.author})

        # Compatibility with `paginator` tag.
        if base['page_obj']:
            base.update({'page': base['page_obj']})

        return base


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
    :param year month day: date matching the `publish_from` field of the `Publishable` object
    :param slug: slug of the `Publishable`
    :param url_remainder: url after the object's url, used to locate custom views in `custom_urls.resolver`

    :raises Http404: if the URL is not valid and/or doesn't correspond to any valid `Publishable`
    """
    template_name = 'object.html'

    class WrongUrl(Http404): pass

    def __call__(self, request, category, slug, year=None, month=None, day=None, id=None, url_remainder=None):
        try:
            context = self.get_context(request, category, slug, year, month, day, id)
        except self.WrongUrl, e:
            message, obj = e.args
            url = obj.get_absolute_url()
            if url_remainder:
                url += url_remainder
            return redirect(url, permanent=True)

        obj = context['object']

        object_rendering.send(sender=context['object'].__class__, request=request, category=context['category'], publishable=context['object'])

        # check for custom actions
        if url_remainder:
            return custom_urls.resolver.call_custom_view(request, obj, url_remainder, context)
        response = render_as_api(request, obj)
        if response:
            return response

        if custom_urls.resolver.has_custom_detail(obj):
            return custom_urls.resolver.call_custom_detail(request, context)

        object_rendered.send(sender=context['object'].__class__, request=request, category=context['category'], publishable=context['object'])

        return self.render(request, context, self.get_templates(context))

    def get_context(self, request, category, slug, year, month, day, id):
        try:
            cat = Category.objects.get_by_tree_path(category)
        except Category.DoesNotExist:
            # non-static url, no way to recover
            if year:
                raise Http404("Category with tree_path '%s' doesn't exist." % category)
            else:
                cat = None

        if year:
            start_date = localize(datetime(int(year), int(month), int(day)))
            end_date = start_date + timedelta(days=1)

            lookup = {
                'publish_from__gte': start_date,
                'publish_from__lt': end_date,
                'category': cat,
                'slug': slug,
                'static': False
            }
            try:
                publishable = get_cached_object(Publishable, published=True, **lookup)
            except Publishable.DoesNotExist:
                # Fallback for staff members in case there are multiple
                # objects with same URL.
                if request.user.is_staff:
                    try:
                        # Make sure we return specific publishable subclass
                        # like when using `get_cached_object` if possible.
                        p = Publishable.objects.filter(published=False, **lookup)[0]
                        publishable = p.content_type.model_class()._default_manager.get(pk=p.pk)
                    except IndexError:
                        raise Http404
                else:
                    raise Http404
        else:
            publishable = get_cached_object_or_404(Publishable, pk=id)

        if not (publishable.is_published() or request.user.is_staff):
            # future publish, render if accessed by logged in staff member
            raise Http404

        if not year:
            if cat is None:
                raise self.WrongUrl('Category with tree_path %r does not exist.' % category, publishable)
            elif not publishable.static:
                raise self.WrongUrl('%s is not static.' % publishable, publishable)
            elif slug != publishable.slug:
                raise self.WrongUrl('Wrong slug in URL (%r).' % slug, publishable)
            elif publishable.category_id != cat.pk:
                raise self.WrongUrl('Wrong category for %s.' % publishable, publishable)

        # save existing object to preserve memory and SQL
        publishable.category = cat

        context = {
            'object': publishable,
            'category': cat,
            'content_type_name': slugify(publishable.content_type.model_class()._meta.verbose_name_plural),
            'content_type': publishable.content_type
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

    All parameters are optional, filtering is done on those supplied

    :raises Http404: if the specified category or content_type does not exist or if the given date is malformed.
    """
    empty_homepage_template_name = 'debug/empty_homepage.html'

    class EmptyHomepageException(Exception): pass

    def __call__(self, request, **kwargs):
        # get the category
        try:
            cat = self.get_category(request, kwargs.pop('category', ''))
        except self.EmptyHomepageException:
            return self.render(request, {}, self.empty_homepage_template_name)

        # mark it as being rendered
        object_rendering.send(sender=Category, request=request, category=cat, publishable=None)
        object_rendered.send(sender=Category, request=request, category=cat, publishable=None)

        # if API enabled and active, return a serialized category
        response = render_as_api(request, cat)
        if response:
            return response

        context = self.get_context(request, cat, **kwargs)

        # custom view for category
        if custom_urls.resolver.has_custom_detail(cat):
            # custom_urls depend on the main rendered object being stored as
            # 'object' in context
            context['object'] = cat
            return custom_urls.resolver.call_custom_detail(request, context)

        template_name = cat.template
        archive_template = cat.app_data.ella.archive_template

        if archive_template and not context.get('is_title_page'):
            template_name = archive_template

        return self.render(request, context, self.get_templates(context, template_name))

    @cache_this(archive_year_cache_key, timeout=60 * 60 * 24)
    def _archive_entry_year(self, category):
        " Return ARCHIVE_ENTRY_YEAR from settings (if exists) or year of the newest object in category "
        year = getattr(settings, 'ARCHIVE_ENTRY_YEAR', None)
        if not year:
            n = now()
            try:
                year = Listing.objects.filter(
                        category__site__id=settings.SITE_ID,
                        category__tree_path__startswith=category.tree_path,
                        publish_from__lte=n
                    ).values('publish_from')[0]['publish_from'].year
            except:
                year = n.year
        return year

    def get_category(self, request, category_path):
        try:
            cat = Category.objects.get_by_tree_path(category_path)
        except Category.DoesNotExist:
            # Homepage behaves differently on 404 with DEBUG mode to let user
            # know everything is fine instead of 404.
            if settings.DEBUG is True and not category_path:
                raise self.EmptyHomepageException()

            raise Http404(_('Category with tree path %(path)r does not exist on site %(site)s') %
                    {'path': category_path, 'site': settings.SITE_ID})
        return cat

    def get_context(self, request, category, year=None, month=None, day=None):

        ella_data = category.app_data.ella

        no_home_listings = ella_data.no_home_listings

        # pagination
        page_no = None
        if 'p' in request.GET and request.GET['p'].isdigit():
            page_no = int(request.GET['p'])

        # if we are not on the first page, display a different template
        category_title_page = (page_no is None or (not no_home_listings and page_no == 1)) and not year

        if page_no is None:
            page_no = 1

        kwa = {'children': ella_data.child_behavior}

        if 'using' in request.GET:
            kwa['source'] = request.GET['using']
        else:
            kwa['source'] = ella_data.listing_handler

        if day:
            try:
                start_day = datetime(int(year), int(month), int(day))
                kwa['date_range'] = (start_day, start_day + timedelta(seconds=24 * 3600 - 1))
            except (ValueError, OverflowError):
                raise Http404(_('Invalid day value %r') % day)
        elif month:
            try:
                start_day = datetime(int(year), int(month), 1)
                kwa['date_range'] = (start_day, (start_day + timedelta(days=32)).replace(day=1) - timedelta(seconds=1))
            except (ValueError, OverflowError):
                raise Http404(_('Invalid month value %r') % month)
        elif year:
            try:
                start_day = datetime(int(year), 1, 1)
                kwa['date_range'] = (start_day, (start_day + timedelta(days=370)).replace(day=1) - timedelta(seconds=1))
            except (ValueError, OverflowError):
                raise Http404(_('Invalid year value %r') % year)

        if 'date_range' in kwa:
            kwa['date_range'] = tuple(map(localize, kwa['date_range']))

        # basic context
        context = {
            'category' : category,
            'is_homepage': category_title_page and not category.tree_parent_id,
            'is_title_page': category_title_page,
            'archive_entry_year' : lambda: self._archive_entry_year(category),
        }

        # no listings wanted on title page
        if category_title_page and no_home_listings:
            return context

        # add pagination
        page = ella_data.get_listings_page(page_no, **kwa)
        context.update({
            'is_paginated': page.has_other_pages(),
            'results_per_page': page.paginator.per_page,
            'page': page,
            'listings': page.object_list,
        })

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

    try:
        cat = Category.objects.get_by_tree_path('')
    except Category.DoesNotExist:
        raise Http404()
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
    response = TemplateResponse(request, 'page/404.html', {})
    response.status_code = 404
    return response.render()

def handle_error(request):
    response = TemplateResponse(request, 'page/500.html', {})
    response.status_code = 500
    return response.render()
