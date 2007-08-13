from django.dispatch import dispatcher
from django.db.models import signals, ObjectDoesNotExist
from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site

from django.db import transaction

OLD_URL_NAME = '__old_url'

from ella.core.cache.invalidate import CACHE_DELETER

def record_url(instance):
    if instance._get_pk_val() and  hasattr(instance, 'get_absolute_url'):
        try:
            old_instance = instance._default_manager.get(pk=instance._get_pk_val())
        except ObjectDoesNotExist:
            return instance
        setattr(instance, OLD_URL_NAME, old_instance.get_absolute_url())
        CACHE_DELETER(instance.__class__, instance)

    return instance

def check_url(instance):
    if hasattr(instance, OLD_URL_NAME):
        new_path = instance.get_absolute_url()
        old_path = getattr(instance, OLD_URL_NAME)

        if old_path != new_path:
            redirect = Redirect(site=Site.objects.get_current(), old_path=old_path, new_path=new_path)
            redirect.save()
            for r in Redirect.objects.filter(new_path=old_path):
                r.new_path = new_path
                r.save()

    return instance

def drop_redirects(instance):
    if hasattr(instance, 'get_absolute_url'):
        Redirect.objects.filter(new_path=instance.get_absolute_url()).delete()

dispatcher.connect(record_url, signal=signals.pre_save)
dispatcher.connect(check_url, signal=signals.post_save)
dispatcher.connect(drop_redirects, signal=signals.pre_delete)
