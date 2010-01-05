from django.utils.translation import ugettext_lazy as _
from ella import newman

from ella.oldcomments.models import Comment, BannedUser, CommentOptions
from django.conf.urls.defaults import patterns, url
from ella.newman.utils import JsonResponse

class CommentAdmin(newman.NewmanModelAdmin):
    list_display = ('subject', 'submit_date', 'target', 'author', 'is_public', 'path',)
    search_fields = ('subject', 'content', 'id',)
    raw_id_fields = ('parent',)
    ordering = ('-submit_date',)

    fieldsets = (
        (_("Deletion"), {'fields': ('is_public',)}),
        (_("Data"), {
            'fields': (
                    'submit_date',
                    'target_ct', 'target_id', 'subject', 'content',
                    'parent', 'user', 'nickname', 'email', 'ip_address',
                    )
        }),
    )

    def get_urls(self):
        urlpatterns = patterns('',
            url(r'^delete-related/(\d+)/(\d+)/$',
                self.delete_related_comments_view,
                name='delete_related_comments'),
        )
        urlpatterns += super(CommentAdmin, self).get_urls()
        return urlpatterns

    def delete_related_comments_view(self, request, ct, id):
        Comment.objects.filter(target_ct=ct, target_id=id).delete()
        return JsonResponse('OK', {})


class CommentoptionsAdmin(newman.NewmanModelAdmin):
    list_display = ('target', 'options', 'timestamp',)
    list_filter = ('target_ct', 'timestamp',)

    def get_urls(self):
        urlpatterns = patterns('',
            url(r'^block/(\d+)/(\d+)/$',
                self.block_comments_view,
                name='block_comment'),
        )
        urlpatterns += super(CommentoptionsAdmin, self).get_urls()
        return urlpatterns

    def block_comments_view(self, request, ct, id):
        data = {
            'target_ct': ct,
            'target_id': id,
            'options': 'OL'
        }
        CommentOptions.objects.get_or_create(**data)
        return JsonResponse('OK', {})

#newman.site.register(Comment, CommentAdmin)
#newman.site.register(BannedUser)
#newman.site.register(CommentOptions, CommentoptionsAdmin)

