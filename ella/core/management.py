from django.dispatch import dispatcher
from django.db.models import signals, ObjectDoesNotExist
from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site

OLD_URL_NAME = '__old_url'


def record_url(instance):
    if instance._get_pk_val() and  hasattr(instance, 'get_absolute_url'):
        try:
            old_instance = instance._default_manager.get(pk=instance._get_pk_val())
        except ObjectDoesNotExist:
            return instance
        setattr(instance, OLD_URL_NAME, old_instance.get_absolute_url())

    return instance

def check_url(instance):
    if hasattr(instance, OLD_URL_NAME):
        new_path = instance.get_absolute_url()
        old_path = getattr(instance, OLD_URL_NAME)

        if old_path != new_path:
            redirect = Redirect(site=Site.objects.get_current(), old_path=old_path, new_path=new_path)
            redirect.save()
    return instance

dispatcher.connect(record_url, signal=signals.pre_save)
dispatcher.connect(check_url, signal=signals.post_save)
