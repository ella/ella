from django.dispatch import dispatcher
from django.db.models import signals


def change_slug(instance):
    if instance._get_pk_val() and  hasattr(instance, 'get_absolute_url'):
        old_instance = instance._default_manager.get(pk=instance._get_pk_val())
        old_path = old_instance.get_absolute_url()
        new_path = instance.get_absolute_url()
        if old_path != new_path:
            pass # create redirect
    return instance

dispatcher.connect(change_slug, signal=signals.pre_save)
