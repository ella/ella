class ReminderLibrary(object):
    def __init__(self):
        self._registry = []

    def register(self, reminder_class):
        self._registry.append(reminder_class)

    def send_all(self, time):
        for rem_cl in self._registry:
            rem_cl._default_manager.send(time)

    @property
    def reminders(self):
        return self._registry

library = ReminderLibrary()
