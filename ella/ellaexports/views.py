from datetime import datetime

from django.http import Http404
from django.conf import settings
#from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from ella.core.models import Category
from ella.core.cache import get_cached_object_or_404
from ella.core.cache.template_loader import render_to_response
from ella.core.views import EllaCoreView
from ella.photos.models import Format
from ella.ellaexports.models import Export, AggregatedExport


def get_templates(name, slug=None, category=None, app_label=None, model_label=None):
    """
    Returns templates in following format and order:

        - 'page/category/%s/content_type/%s.%s/%s/%s' % ( category.path, app_label, model_label, slug, name ),
        - 'page/category/%s/content_type/%s.%s/%s' % ( category.path, app_label, model_label, name ),
        - 'page/category/%s/%s' % ( category.path, name ),
        - 'page/content_type/%s.%s/%s/%s' % ( app_label, model_label, slug, name ),
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
        if category.tree_parent:
            templates.append('page/category/%s/%s' % (category.tree_parent.path, name))
    if app_label and model_label:
        if slug:
            templates.append('page/content_type/%s.%s/%s/%s' % (app_label, model_label, slug, name))
        templates.append('page/content_type/%s.%s/%s' % (app_label, model_label, name))
    templates.append('page/%s' % name)
    return templates

class MrssExport(EllaCoreView):
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
        .. name = export.xml
    """

    template_name = 'export.xml'

    def get_templates(self, context, template_name=None):
        " Extract parameters for `get_templates` from the context. "
        kw = {}
        if 'export_slug' in context:
            kw['slug'] = context['export_slug']

        if context.get('content_type', False):
            ct = context['content_type']
            kw['app_label'] = ct.app_label
            kw['model_label'] = ct.model
        else:
            kw['app_label'] = Export._meta.app_label
            kw['model_label'] = Export._meta.module_name

        return get_templates(self.template_name, category=context['category'], **kw)

    def get_context(self, request, **kwargs):
        now = datetime.now()
        category = kwargs.get('category', None)
        slug = kwargs.get('slug', None)
        export = None
        export_object = None
        cat = None
        title = u''
        link = ''
        items = tuple()
        context = dict()

        photo_format = request.GET.get('photo_format', None)
        if photo_format:
            try:
                photo_format = get_cached_object_or_404(Format, name=photo_format, sites=settings.SITE_ID)
            except ValueError, Format.DoesNotExist:
                raise Http404
        else:
            photo_format = None

        if slug:
            items = Export.objects.get_items_for_slug(slug=slug, photo_format=photo_format)
            try:
                export_object = Export.objects.get(slug=slug)
            except Export.DoesNotExist:
                raise Http404(_('Export with given slug does not exist.'))
        else:
            if category:
                cat = get_cached_object_or_404(Category, tree_path=category, site__id=settings.SITE_ID)
            else:
                cat = get_cached_object_or_404(Category, tree_parent__isnull=True, site__id=settings.SITE_ID)
            items = Export.objects.get_items_for_category(category=cat, photo_format=photo_format)
            export_object = Export.objects.get(category=cat)

        # Ugly hack how to force photo format passed in GET params
        if photo_format:
            export_object.photo_format = photo_format

        title = export_object.title
        link = export_object.url
        description = export_object.description

        context.update({
            'updated': now.strftime('%Y-%m-%dT%H:%M:%S+02:00'),
            'exported_items': items,
            'export_slug': slug,
            'export_object': export_object,
            'description': description,
            'category': cat,
            'is_homepage': not bool(category),
            'title': title,
            'link': link
        })
        return context

    def render(self, request, context, template):
        return render_to_response(
            template, 
            context,
            context_instance=RequestContext(request),
            content_type='application/xml'
        )

    #def __call__(self, *args, **kwargs):
    #    super(MrssExport, self).__call__(*args, **kwargs)

mrss_export = MrssExport()

class AggregatedMrssExport(MrssExport):
    template_name = 'aggregated_export.xml'

    def get_context(self, request, **kwargs):
        slug = kwargs.get('slug', None)
        export_object = get_cached_object_or_404(AggregatedExport, slug=slug)

        context = {
            'export_slug': slug,
            'export_object': export_object,
            'category': None
        }
        return context

aggregated_export = AggregatedMrssExport()


# EOF
