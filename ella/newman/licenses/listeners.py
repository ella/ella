import logging

from django import template
from django.db.models import signals
from django.contrib.contenttypes.models import ContentType

from ella.core.models.main import Dependency

log = logging.getLogger('ella.newman.licenses')

class LicenseListenerPostSave(object):
    def __init__(self, src_text):
        super(LicenseListenerPostSave, self).__init__()
        self.src_text = src_text

    def __call__(self, sender, signal, created, **kwargs):
        """ TODO:
        Listener na licence je v ella.newman.listeners, je tam mazani deps, pak to chce vzit content 
        jako sablonu a pres nody zjistit boxy a znovuvytvorit deps.
        """
        log.debug('LicenseListener activated by %s, sig=%s, created=%s' % (sender, signal, created))
        log.debug('LicenseListener kwargs=%s' % kwargs)
        src_text = self.src_text

        signals.post_save.disconnect(receiver=self, sender=src_text.content_type.model_class())
        log.debug('Signal listener disconnected')
        target_instance = kwargs['instance']

        # Delete all dependencies for sender instance
        ct = ContentType.objects.get_for_model(sender)
        Dependency.objects.filter(target_ct=ct.pk, target_id=target_instance.pk).delete()

        # Parse text and recreate dependencies
        content = getattr(target_instance, src_text.field)

        log.debug('Dependencies for %s:%d was recreated.' % (ct, target_instance.pk))
