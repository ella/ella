from django.contrib import admin

from ella.reminder.models import DeliveryMethod, Contact, CalendarSubscription, Calendar, Event

admin.site.register([DeliveryMethod, Contact, CalendarSubscription, Calendar, Event])
