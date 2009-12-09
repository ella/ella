from django.contrib import admin
from ella.sample.models import Spam, Type

admin.site.register([Spam, Type])

