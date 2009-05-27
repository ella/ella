from django.contrib import admin
from djangobaselibrary.sample.models import Spam, Type

admin.site.register([Spam, Type])

