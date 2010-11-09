from django.utils.translation import ugettext_lazy as _, ungettext
from django.conf import settings

from ella import newman
from ella.ellacomments.models import CommentOptionsObject, BannedIP

from threadedcomments.models import ThreadedComment
from threadedcomments.admin import ThreadedCommentsAdmin

class CommentOptionsGenericInline(newman.GenericStackedInline):
    ct_field = "target_ct"
    ct_fk_field = "target_id"
    model = CommentOptionsObject

    max_num = 1

class ThreadedCommentsNewmanAdmin(ThreadedCommentsAdmin, newman.NewmanModelAdmin):
    actions = ['approve_comments', 'remove_comments']

    def get_actions(self, request):
        actions = super(ThreadedCommentsNewmanAdmin, self).get_actions(request)
        if not request.user.has_perm('comments.can_moderate'):
            del actions['approve_comments']
            del actions['remove_comments']
        return actions

    def approve_comments(self, request, queryset):
        n_comments = queryset.update(is_removed=False, is_public=True)
        msg = ungettext(u'1 comment was successfully approved.',
            u'%(count)s comments were successfully approved.',
            n_comments)
        self.message_user(request, msg % {'count': n_comments})
    approve_comments.short_description = _('Approve selected comments')

    def remove_comments(self, request, queryset):
        n_comments = queryset.update(is_removed=True)
        msg = ungettext(u'1 comment was successfully removed.',
            u'%(count)s comments were successfully removed.',
            n_comments)
        self.message_user(request, msg % {'count': n_comments})
    remove_comments.short_description = _('Remove selected comments')

class BannedIPNewmanAdmin(newman.NewmanModelAdmin):
    list_display = ('__unicode__', 'created', 'reason')
    list_filter = ('created',)

MODELS_WITH_COMMENTS = getattr(settings, 'MODELS_WITH_COMMENTS', ('articles.article', 'galleries.gallery', 'interviews.interview', ))

newman.site.register(ThreadedComment, ThreadedCommentsNewmanAdmin)
newman.site.append_inline(MODELS_WITH_COMMENTS, CommentOptionsGenericInline)
newman.site.register(BannedIP, BannedIPNewmanAdmin)

# threadedcomments translations for newman
app, n, vn = _('Threadedcomments'), _('Threaded comment'), _('Threaded comments')
