from django.contrib import admin

from ella.media.encoder.models import Format, FormattedFile


admin.site.register([Format, FormattedFile])

