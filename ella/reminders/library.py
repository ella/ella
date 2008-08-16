from django.template.defaultfilters import slugify
from django.db.models import ObjectDoesNotExist

class ReminderLibrary(object):
    def __init__(self):
        self._registry = {}

    def register(self, reminder_class):
        self._registry[slugify(reminder_class._meta.verbose_name_plural)] = reminder_class

    def send_all(self, time):
        for reminder in self._registry.values():
            reminder._default_manager.send(time)

    def get_reminder_class(self, slug):
        try:
            return self._registry[slug]
        except KeyError, e:
            raise ObjectDoesNotExist, 'No reminder with slug %r' % slug

    @property
    def reminders(self):
        return [ r._meta.verbose_name_plural for r in self._registry.values() ]

library = ReminderLibrary()
