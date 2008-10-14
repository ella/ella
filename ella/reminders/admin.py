from django.contrib import admin

from ella.ellaadmin.options import EllaAdminOptionsMixin
from ella.reminders.models import DeliveryMethod, Contact, Calendar, Event

class EventAdmin(EllaAdminOptionsMixin, admin.ModelAdmin):
    list_display = ('title', 'calendar', 'date',)
    search_fields = ('title',)
    list_filter = ('calendar', 'date',)
    rich_text_fields = {None: ('description', 'text',)}

admin.site.register(Event, EventAdmin)
admin.site.register([DeliveryMethod, Contact, Calendar])
