"""
First semi-working draft of category-based permissions. It will allow permissions to be set per-site and per category
effectively hiding the content the user has no permission to see/change.
"""
from django.contrib.admin import filterspecs
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission

from ella.core.models import Category

def get_content_types(user):
    '''return all accessible content types for given user'''
    if user.is_superuser:
        return list(ContentType.objects.all())

    perms = user.get_all_permissions()
    cts = set([])
    for p in perms:
        app_label, perm = p.split('.', 1)
        perm, model = perm.split('_', 1)
        if perm in ('change', 'view',):
            cts.add((app_label, model))
    choices = [ ContentType.objects.get(app_label=app_label, model=model) for (app_label, model) in cts ]
    choices.sort(key=str)
    return choices

class DistinctRelatedFilterSpec(filterspecs.RelatedFilterSpec):
    " Only display models that appear somewhere. "
    def __init__(self, f, request, params, model, model_admin, field_path=None):
        super(DistinctRelatedFilterSpec, self).__init__(f, request, params, model, model_admin, field_path=field_path)
        if field_path is None:
            self.lookup_choices = f.rel.to._default_manager.filter(pk__in=[ d[f.name] for d in model._default_manager.distinct().order_by().values(f.name) ])

class CategoryFilterSpec(DistinctRelatedFilterSpec):
    " FilterSpec for admin that only display's categories the user has permission for. "
    def __init__(self, f, request, params, model, model_admin, field_path=None):
        super(CategoryFilterSpec, self).__init__(f, request, params, model, model_admin, field_path=field_path)
        if request.user.is_superuser:
            return

        from ella.ellaadmin import models
        from django.db.models import Q
        sites = models.applicable_sites(request.user)
        categories = models.applicable_categories(request.user)

        if sites or categories:
            # TODO: terrible hack for circumventing invalid Q(__in=[]) | Q(__in=[])
            self.lookup_choices = Category.objects.filter(Q(pk__in=categories) | Q(site__in=sites))
        else:
            self.lookup_choices = []

class ContentTypeFilterSpec(DistinctRelatedFilterSpec):
    ' Display only applicable content types. '
    def __init__(self, f, request, params, model, model_admin, field_path=None):
        super(ContentTypeFilterSpec, self).__init__(f, request, params, model, model_admin, field_path=field_path)
        self.lookup_choices = self.lookup_choices.filter(pk__in=[ ct.id for ct in get_content_types(request.user) ])


from django.db import models
filterspecs.FilterSpec.register(lambda f: bool(f.rel) and not isinstance(f, models.ManyToManyField), DistinctRelatedFilterSpec)
filterspecs.FilterSpec.register(lambda f: bool(f.rel) and f.rel.to == ContentType, ContentTypeFilterSpec)
#filterspecs.FilterSpec.register(lambda f: bool(f.rel) and  f.rel.to == Category, CategoryFilterSpec)

