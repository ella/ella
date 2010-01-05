from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from django.conf.urls.defaults import patterns, url

from ella.core.custom_urls import resolver
from ella.oldcomments.views import new_comment, CommentFormPreview, list_comments
from ella.oldcomments.forms import CommentForm

urlpatterns = patterns('',
    url(r'^$', list_comments, name='comments-list'),
    url(r'^%s/(?P<reply>\d+)/$' % slugify(_('reply')), new_comment, name='comments-reply'),
    url(r'^%s/$' % slugify(_('new')), new_comment, name='comments-new'),
    url(r'^%s/$' % slugify(_('preview')), CommentFormPreview(CommentForm), name='comments-reply'),

)

resolver.register(urlpatterns, prefix=slugify(_('comments')))

