'''
Created on 5.6.2012

@author: xaralis
'''
from datetime import datetime, timedelta

from django.conf import settings
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.http import Http404
from django.shortcuts import redirect
from django.template.defaultfilters import slugify
from django.template.response import TemplateResponse
from django.views.generic.base import View, TemplateResponseMixin

from ella.core import custom_urls
from ella.core.cache.utils import get_cached_object_or_404, cache_this
from ella.core.conf import core_settings
from ella.core.managers import ListingHandler
from ella.core.models import Category, Publishable, Listing
from ella.core.signals import object_rendering, object_rendered


__docformat__ = "restructuredtext en"

# local cache for get_content_type()
CONTENT_TYPE_MAPPING = {}


class EllaBaseMixin(object):
    category_url_kwarg = 'category'
    year_url_kwarg = 'year'
    month_url_kwarg = 'month'
    day_url_kwarg = 'day'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'id'
    url_remainder_kwarg = 'url_remainder'
    ct_kwarg = 'ct'

    def get_category(self):
        category = self.kwargs.get(self.category_url_kwarg)

        try:
            return Category.objects.get_by_tree_path(category)
        except Category.DoesNotExist:
            raise Http404("Category with tree_path '%s' doesn't exist."
                          % category)


class EllaTemplateResponseMixin(EllaBaseMixin, TemplateResponseMixin):
    FULL = ('page/category/%(pth)s/content_type/'
            '%(app_label)s.%(model_label)s/%(slug)s/%(name)s')
    FULL_NO_SLUG = ('page/category/%(pth)s/content_type/'
                    '%(app_label)s.%(model_label)s/%(name)s')
    BY_CATEGORY = 'page/category/%(pth)s/%(name)s'
    BY_CONTENT_TYPE = ('page/content_type/'
                       '%(app_label)s.%(model_label)s/%(name)s')

    def get_base_template_name(self):
        return self.template_name

    def get_template_names(self):
        """
        Returns templates in following format and order:

        * ``'page/category/%s/content_type/%s.%s/%s/%s' % (<CATEGORY_PART>,
                                                           app_label,
                                                           model_label,
                                                           slug, name)``
        * ``'page/category/%s/content_type/%s.%s/%s' % (<CATEGORY_PART>,
                                                        app_label,
                                                        model_label,
                                                        name)``
        * ``'page/category/%s/%s' % (<CATEGORY_PART>, name)``
        * ``'page/content_type/%s.%s/%s' % (app_label, model_label, name)``
        * ``'page/%s' % name``

        Where ``<CATEGORY_PART>`` is derived from ``path`` attribute by
        these rules:

        * When **no** parent exists (this is therfore root category)
          ``<CATEGORY_PART> = path``
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
        * For **NESTED2**, ``<CATEGORY_PART>`` has two elements:
          "NESTED1/NESTED2" and "NESTED1".
        """
        def category_templates(category, incomplete_template, params):
            paths = []
            parts = category.path.split('/')
            for i in reversed(range(1, len(parts) + 1)):
                params.update({'pth': '/'.join(parts[:i])})
                paths.append(incomplete_template % params)
            return paths

        templates = []
        params = {'name': self.get_base_template_name()}

        if hasattr(self, 'object') and hasattr(self.object, '_meta'):
            app_label = self.object._meta.app_label
            model_label = self.object._meta.object_name.lower()
        else:
            app_label, model_label = None, None

        slug = self.kwargs.get(self.slug_url_kwarg, None)
        category = self.kwargs.get(self.category_url_kwarg, None)

        if app_label and model_label:
            params.update({'app_label': app_label, 'model_label': model_label})

        if slug:
            params.update({'slug': slug})

        if category:
            if app_label and model_label:
                if slug:
                    templates += category_templates(category, self.FULL,
                                                    params)
                templates += category_templates(category, self.FULL_NO_SLUG,
                                                params)
            templates += category_templates(category, self.BY_CATEGORY, params)

        if app_label and model_label:
            templates.append(self.BY_CONTENT_TYPE % params)

        templates.append('page/%(name)s' % params)
        return templates


class ObjectDetail(EllaTemplateResponseMixin, View):
    template_name = 'object.html'

    def get(self, request, *args, **kwargs):
        self.category = self.get_category()
        self.object = self.get_object()

        context = self.get_context_data(object=self.object)

        if (self.object.static and
            kwargs.get(self.slug_url_kwarg) != self.object.slug):
            return redirect(self.object.get_absolute_url(), permanent=True)

        render_params = {
            'sender': self.object.__class__,
            'request': request,
            'category': self.category,
            'publishable': self.object
        }

        # Send pre-rendering signal.
        object_rendering.send(**render_params)

        # Check for custom actions on the Publishable object.
        url_remainder = kwargs.get(self.url_remainder_kwarg, None)

        if url_remainder is not None:
            return custom_urls.resolver.call_custom_view(
                request, self.object, url_remainder, context)
        elif custom_urls.resolver.has_custom_detail(self.object):
            return custom_urls.resolver.call_custom_detail(request, context)

        # Send post-rendering signal.
        object_rendered.send(**render_params)

        return self.render_to_response(context)

    def get_object(self):
        year = self.kwargs.get(self.year_url_kwarg, None)

        if year is not None:
            month = self.kwargs.get(self.month_url_kwarg)
            day = self.kwargs.get(self.day_url_kwarg)
            slug = self.kwargs.get(self.slug_url_kwarg)

            publishable = get_cached_object_or_404(Publishable,
                publish_from__year=year,
                publish_from__month=month,
                publish_from__day=day,
                category=self.category,
                slug=slug,
                static=False
            )
        else:
            pk = self.kwargs.get(self.pk_url_kwarg)
            publishable = get_cached_object_or_404(Publishable, pk=pk)

            if (publishable.category_id != self.category.pk or
                not publishable.static):
                raise Http404()

        # Cast from Publishable.
        obj = publishable.target

        # Save existing object to preserve memory and SQL.
        obj.category = self.category

        if not (obj.is_published() or self.request.user.is_staff):
            # future publish, render if accessed by logged in staff member
            raise Http404

        return obj

    def get_context_data(self, **kwargs):
        context = {
            'object': kwargs.pop('object'),
            'category': self.category,
            'content_type_name': slugify(
                self.object.content_type.model_class()._meta.verbose_name_plural),
            'content_type': self.object.content_type
        }
        context.update(kwargs)
        return context


def archive_year_cache_key(self, category):
    return 'core.archive_year:%d' % category.pk


class ListContentType(EllaTemplateResponseMixin, View):
    archive_template_name = 'listing.html'
    empty_homepage_template_name = 'debug/empty_homepage.html'
    pagination_url_arg = 'p'

    def get(self, request, *args, **kwargs):
        self.category = self.get_category()
        self.object_list = self.get_object_list()

        context = self.get_context_data()

        rendering_params = {
            'sender': Category,
            'request': request,
            'category': self.category,
            'publishable': None
        }

        object_rendering.send(**rendering_params)
        object_rendered.send(**rendering_params)

        return self.render_to_response(context)

    def get_object_list(self):
        year = self.kwargs.get(self.year_url_kwarg, None)
        month = self.kwargs.get(self.month_url_kwarg)
        day = self.kwargs.get(self.day_url_kwarg)

        ella_data = self.category.app_data['ella']
        no_home_listings = ella_data.get('no_home_listings',
                                         core_settings.CATEGORY_NO_HOME_LISTINGS)

        # pagination
        if (self.pagination_url_arg in self.request.GET and
            self.request.GET[self.pagination_url_arg].isdigit()):
            self.page_no = int(self.request.GET[self.pagination_url_arg])

        self.is_title_page = ((self.page_no is None or
                              (not no_home_listings and self.page_no == 1))
                              and not year)
        self.is_homepage = (not bool(self.category) and
                            self.page_no == 1 and
                            year is None)

        if self.page_no is None:
            self.page_no = 1

        kwa = {'category': self.category}
        if day:
            try:
                sday = datetime(int(year), int(month), int(day))
                kwa['date_range'] = (sday,
                                     sday + timedelta(seconds=24 * 3600 - 1))
            except (ValueError, OverflowError):
                raise Http404(_('Invalid day value %r') % day)
        elif month:
            try:
                sday = datetime(int(year), int(month), 1)
                eday = ((sday + timedelta(days=32)).replace(day=1) -
                        timedelta(seconds=1))
                kwa['date_range'] = (sday, eday)
            except (ValueError, OverflowError):
                raise Http404(_('Invalid month value %r') % month)
        elif year:
            try:
                sday = datetime(int(year), 1, 1)
                eday = ((sday + timedelta(days=370)).replace(day=1) -
                        timedelta(seconds=1))
                kwa['date_range'] = (sday, eday)
            except (ValueError, OverflowError):
                raise Http404(_('Invalid year value %r') % month)

        if 'date_range' in kwa:
            kwa['date_range'] = tuple(map(utc_localize, kwa['date_range']))

        if self.kwargs[self.category_url_kwarg]:
            kwa['children'] = ListingHandler.ALL

        if 'using' in self.kwargs:
            kwa['source'] = self.kwargs.get('using')
        else:
            kwa['source'] = ella_data.get('listing_handler', 'default')

        self.paginate_by = ella_data.get('paginate_by', core_settings.CATEGORY_LISTINGS_PAGINATE_BY)

        # Collect all the objects. Store paginator and page objects.
        self.paginator = Paginator(Listing.objects.get_queryset_wrapper(**kwa),
                                   self.paginate_by)
        if self.page_no > self.paginator.num_pages or self.page_no < 1:
            raise Http404(_('Invalid page number %r') % self.page_no)
        self.page = self.paginator.page(self.page_no)

        # Finally get object list, keep ``is_empty`` sign and return.
        object_list = self.page.object_list
        self.is_empty = bool(object_list)

        return object_list

    def get_context_data(self, **kwargs):
        context = {
            'category': self.category,
            'is_homepage': self.is_homepage,
            'is_title_page': self.is_title_page,
            'is_paginated': self.paginator.num_pages > 1,
            'results_per_page': self.paginate_by,
            'page': self.page,
            'listings': self.object_list,
            'archive_entry_year': lambda: self._archive_entry_year(self.category),
        }
        context.update(kwargs)
        return context

    def get_base_template_name(self):
        # Homepage is considered when category is empty (~ no slug) and no
        # filtering is used.
        #
        # Homepage behaves differently on 404 with DEBUG mode to let user
        # know everything is fine instead of 404. Also, indication of
        # homepage is added to context, it's usually good to know, if your
        # on homepage, right? :)
        if self.is_homepage and self.is_empty and settings.DEBUG:
            return self.empty_homepage_template_name

        # If we are not on the first page, display a different template.
        if core_settings.ARCHIVE_TEMPLATE and not self.is_title_page:
            return self.archive_template_name

        return self.category.template

    @cache_this(archive_year_cache_key, timeout=60 * 60 * 24)
    def _archive_entry_year(self, category):
        """Return ARCHIVE_ENTRY_YEAR from settings (if exists) or year of the
        newest object in category """
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


def page_not_found(request):
    response = TemplateResponse(request, 'page/404.html', {})
    response.status_code = 404
    return response


def handle_error(request):
    response = TemplateResponse(request, 'page/500.html', {})
    response.status_code = 500
    return response
