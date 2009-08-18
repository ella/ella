from django.utils.translation import ugettext_lazy as _
from ella import newman

from ella.comments.models import Comment, BannedUser, CommentOptions

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

newman.site.register(Comment, CommentAdmin)
newman.site.register(BannedUser)
newman.site.register(CommentOptions)

