from django.conf.urls.defaults import *
from nc.comments.forms import CommentForm, CommentFormPreview

urlpatterns = patterns('',
        url(r'^.*$', CommentFormPreview(CommentForm)),
)

