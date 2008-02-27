from django.dispatch import dispatcher
from django.db.models import signals, ObjectDoesNotExist
from django.contrib.redirects.models import Redirect
from django.conf import settings

from ella.core.cache.invalidate import CACHE_DELETER


# name of attribute used to store object's old URL
OLD_URL_NAME = '__old_url'


def record_url(instance):
    """
    Check if the object being changed has get_absolute_url(), if so store its value
    for check_url.
    """
    if instance._get_pk_val() and  hasattr(instance, 'get_absolute_url'):
        try:
            old_instance = instance._default_manager.get(pk=instance._get_pk_val())
        except ObjectDoesNotExist:
            return instance
        try:
            url = old_instance.get_absolute_url()
            if url is not None:
                setattr(instance, OLD_URL_NAME, url)
                CACHE_DELETER(instance.__class__, instance)
        except:
            # if something goes wrong with the object, not catching the exception here
            # will cause the save() to fail, thus preventing anybody from correcting the error
            pass

    return instance

def check_url(instance):
    """
    Check if the object that was just changed has a OLD_URL_NAME set on it. If so compareit with its current absolute_url
    and create a redirect object if necessary.
    """
    if hasattr(instance, OLD_URL_NAME):
        new_path = instance.get_absolute_url()
        old_path = getattr(instance, OLD_URL_NAME)

        if old_path != new_path and new_path:
            redirect, created = Redirect.objects.get_or_create(old_path=old_path, new_path=new_path, defaults={'site_id' : settings.SITE_ID})
            for r in Redirect.objects.filter(new_path=old_path):
                r.new_path = new_path
                r.save()

    return instance

def drop_redirects(instance):
    """
    If an object is deleted, delete all its redirects.
    """
    if hasattr(instance, 'get_absolute_url'):
        try:
            Redirect.objects.filter(new_path=instance.get_absolute_url()).delete()
        except:
            # if something goes wrong with the object, not catching the exception here
            # will cause the save() to fail, thus preventing anybody from correcting the error
            pass


dispatcher.connect(record_url, signal=signals.pre_save)
dispatcher.connect(check_url, signal=signals.post_save)
dispatcher.connect(drop_redirects, signal=signals.pre_delete)

