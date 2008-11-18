from django.contrib import admin

from ella.contact_form.models import Recipient, Message

admin.site.register((Recipient, Message))
