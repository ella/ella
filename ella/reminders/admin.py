from django.contrib import admin

from ella.reminders.models import DeliveryMethod, Contact, Calendar, Event

admin.site.register([DeliveryMethod, Contact, Calendar, Event])
