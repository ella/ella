from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from ella.oldcomments.models import Comment, BannedUser, CommentOptions
from ella.ellaadmin.options import EllaAdminOptionsMixin

class CommentsOptions(EllaAdminOptionsMixin, admin.ModelAdmin):
    ordering = ('-submit_date',)
    list_display = ('subject', 'submit_date', 'target', 'author', 'is_public', 'path',)
    search_fields = ('subject', 'content', 'id',)
    raw_id_fields = ('parent',)
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

admin.site.register(Comment, CommentsOptions)
admin.site.register(BannedUser)
admin.site.register(CommentOptions)

