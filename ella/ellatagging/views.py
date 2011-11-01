"""
Tagging related views.
"""
from datetime import datetime

from django.template.defaultfilters import slugify
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.views.generic import ListView
from django.conf import settings

from tagging.models import Tag, TaggedItem

from ella.core.models import Publishable


def get_tagged_publishables(tag):
    now = datetime.now()
    queryset = Publishable.objects.filter(
        Q(placement__publish_to__isnull=True) | Q(placement__publish_to__gt=now),
        placement__publish_from__lt=now).distinct()
    return TaggedItem.objects.get_by_model(queryset, tag)


class TaggedPublishablesView(ListView):
    context_object_name = 'object_list'
    paginate_by = getattr(settings, 'TAG_LISTINGS_PAGINATE_BY', 10)

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, name=self.kwargs['tag'])
        return get_tagged_publishables(self.tag)

    def get_template_names(self):
        return [
            'page/tagging/%s/listing.html' % slugify(self.kwargs['tag']),
            'page/tagging/listing.html',
        ]

    def paginate_queryset(self, queryset, page_size):
        """
        Ella uses it's own pagination style. If you want django's style,
        delete this function.
        """
        paginator = self.get_paginator(queryset,
                                       page_size,
                                       allow_empty_first_page=self.get_allow_empty())

        if 'p' in self.request.GET and self.request.GET['p'].isdigit():
            page_no = int(self.request.GET['p'])
        else:
            page_no = 1

        page = paginator.page(page_no)
        return (paginator, page, page.object_list, page.has_other_pages())

    def get_context_data(self, **kwargs):
        context = super(TaggedPublishablesView, self).get_context_data(**kwargs)
        if context['is_paginated']:
            context['page'] = context['page_obj']
            context['results_per_page'] = self.paginate_by

        context['tag'] = self.tag
        return context
