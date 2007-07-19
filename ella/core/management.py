from django.dispatch import dispatcher
from django.db.models import signals, ObjectDoesNotExist


def change_slug(instance):
    if instance._get_pk_val() and  hasattr(instance, 'get_absolute_url'):
        try:
            old_instance = instance._default_manager.get(pk=instance._get_pk_val())
        except ObjectDoesNotExist:
            return instance
        old_path = old_instance.get_absolute_url()
        new_path = instance.get_absolute_url()
        if old_path != new_path:
            pass # create redirect
    return instance

dispatcher.connect(change_slug, signal=signals.pre_save)
