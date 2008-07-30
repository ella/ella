from datetime import datetime, date

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

from ella.reminders.library import library

class DeliveryMethod(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=255)

    function = models.CharField(_('Function'), max_length=255)

    def get_function(self):
        if not hasattr(self, '_function'):
            mod = __import__('.'.join(self.function.split('.')[:-1]), {}, {}, [self.function.split('.')[-1]])
            self._function = getattr(mod, self.function.split('.')[-1])
        return self._function

    def send(self, contact, reminder, event, date):
        self.get_function()(
            contact.contact,
            render_to_string(
                (
                    'reminders/reminder/%s/method/%s/%s.html' % (reminder.slug, self.slug, event.slug),
                    'reminders/reminder/%s/method/%s/event.html' % (reminder.slug, self.slug,),
                    'reminders/method/%s/event.html' % (self.slug,),
                    'reminders/reminder/%s/event.html' % (reminder.slug,),
                    'reminders/event.html',
),
                {
                    'reminder': reminder,
                    'event': event,
                    'contact': contact,
                    'date': date
}
)
)

class Contact(models.Model):
    user = models.ForeignKey(User)
    contact = models.CharField(_('Contact'), max_length=255)

    delivery_method = models.ForeignKey(DeliveryMethod)

    def __unicode__(self):
        return unicode(self.user)

    class Meta:
        unique_together = (('user', 'delivery_method',),)



### One specific implementation
###############################################################################


#class CalendarSubscription(models.Model):
#    calendar = models.ForeignKey(Calendar)
#    contact = models.ForeignKey(Contact)


class CalendarManager(models.Manager):
    def send(self, time):
        date = time.date()
        for e in Event.objects.filter(date=date).select_related('calendar'):
            for c in e.calendar.subscribers.all():
                # TODO: GROUP BY delivery_method and do batch sending
                c.delivery_method.send(c, e.calendar, e, date)

class Calendar(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=255)

    created = models.DateTimeField(_('Created'), default=datetime.now, editable=False)
    subscribers = models.ManyToManyField(Contact)#, via=CalendarSubscription)

    objects = CalendarManager()

    def subscribe(self, contact):
        self.subscribers.add(contact)

    def unsubscibe(self, user):
        self.subscribers.filter(contact__user=user).delete()

    class Meta:
        verbose_name = _('Reminder')
        verbose_name_plural = _('Reminders')
        ordering = ('-created',)

    def __unicode__(self):
        return self.title

library.register(Calendar)

class Event(models.Model):
    # make this publishable ??
    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=255)

    calendar = models.ForeignKey(Calendar)
    date = models.DateField(_('Date'))

    description = models.TextField()
    text = models.TextField()

    class Meta:
        ordering = ('-date',)
        verbose_name = _('Event')
        verbose_name_plural = _('Events')


