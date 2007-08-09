from django.conf.urls.defaults import *
from ella.comments.views import comment_preview

urlpatterns = patterns('',
        url(r'^', comment_preview, name="comment"),
)

