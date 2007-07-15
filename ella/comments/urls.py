from django.conf.urls.defaults import *
from ella.comments.forms import CommentForm, CommentFormPreview

urlpatterns = patterns('',
        url(r'^', CommentFormPreview(CommentForm), name="comment"),
)

