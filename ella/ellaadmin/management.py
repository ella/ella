"""
Copied over from django.contrib.auth.management
"""
from django.dispatch import dispatcher
from django.db.models import get_models, signals

def _get_permission_codename(action, opts):
    return u'%s_%s' % (action, opts.object_name.lower())

def _get_all_permissions(opts):
    "Returns (codename, name) for all permissions in the given opts."
    return [ (_get_permission_codename('view', opts), u'Can view %s' % (opts.verbose_name_raw)), ]

def create_permissions(app, created_models, verbosity):
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.auth.models import Permission
    app_models = get_models(app)
    if not app_models:
        return
    for klass in app_models:
        ctype = ContentType.objects.get_for_model(klass)
        for codename, name in _get_all_permissions(klass._meta):
            p, created = Permission.objects.get_or_create(codename=codename, content_type__pk=ctype.id,
                defaults={'name': name, 'content_type': ctype})
            if created and verbosity >= 2:
                print "Adding permission '%s'" % p

dispatcher.connect(create_permissions, signal=signals.post_syncdb)

