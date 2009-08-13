from django.http import Http404
from django.conf import settings
from django.template.defaultfilters import slugify

from ella.core.models import Listing, Category, Placement
from ella.core.cache import get_cached_object_or_404, cache_this
from ella.core.cache.template_loader import render_to_response
from ella.core.views import get_templates, EllaCoreView
from ella.exports.models import Export, ExportMeta, ExportPosition
from ella.exports.models import UnexportableException


class MrssExports(EllaCoreView):
    """
    1. URL format is /category/path/to/any/depth/[content_type/]
    2. Sort export items by its main placement and listings.
    3. Override item's title, photo, description if ExportMeta for item and Export is present.
    4. Override item's position and visibility timerange if defined.

    Template discover-order is as same as in case of Ella views:
        'page/category/%s/content_type/%s.%s/%s/%s' % ( category.path, app_label, model_label, slug, name ),
        'page/category/%s/content_type/%s.%s/%s' % ( category.path, app_label, model_label, name ),
        'page/category/%s/%s' % ( category.path, name ),
        'page/content_type/%s.%s/%s' % ( app_label, model_label, name ),
        'page/%s' % name,
        .. name = mrss_export.html
    """

    template_name = 'mrss_export.html'

    def __get_templates(self, context):
        " Extract parameters for `get_templates` from the context. "
        kw = {}
        if 'object' in context:
            o = context['object']
            kw['slug'] = o.slug

        if context.get('content_type', False):
            ct = context['content_type']
            kw['app_label'] = ct.app_label
            kw['model_label'] = ct.model

        return get_templates(self.template_name, category=context['category'], **kw)

    def get_context(self, request, **kwargs):
        category = kwargs.get('category', None)
        slug = kwargs.get('slug', None)
        export = None
        cat = None
        title = u''
        link = ''
        items = tuple()
        context = dict()

        if slug:
            items = Export.objects.get_items_for_slug(slug=slug)
            try:
                export_object = Export.objects.get(slug=slug)
                title = export_object.title
                link = export_object.url
            except Export.DoesNotExist:
                raise Http404
        else:
            if category:
                cat = get_cached_object_or_404(Category, tree_path=category, site__id=settings.SITE_ID)
            else:
                cat = get_cached_object_or_404(Category, tree_parent__isnull=True, site__id=settings.SITE_ID)
            items = Export.objects.get_items_for_category(category=cat)
            export_object = Export.objects.get(category=cat)
            title = export_object.title
            link = export_object.url

        context.update({
            'exported_items': items,
            'category': cat,
            'is_homepage': not bool(category),
            'title': title,
            'link': link
        })
        return context

mrss_exports = MrssExports()

# EOF
