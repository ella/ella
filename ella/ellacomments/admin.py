from django.contrib import admin
from django.contrib.contenttypes.generic import GenericInlineModelAdmin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode

from ella.ellacomments.models import CommentOptionsObject, BannedIP
from threadedcomments.admin import ThreadedCommentsAdmin
from threadedcomments.models import ThreadedComment

class CommentOptionsGenericInline(GenericInlineModelAdmin):
    model = CommentOptionsObject
    max_num = 1


class CommentsAdmin(ThreadedCommentsAdmin):
    def __call__( self, request, url ):
        import sys
        if url and url.startswith( 'deleterelated' ):
            return self.delete_related( request, *url.split('/')[1:] )
        if url and url.startswith( 'info' ):
            return self.json_info( request, *url.split('/')[1:] )
        return super( CommentsAdmin, self ).__call__( request, url )

    def delete_related(self, request, ct, id):
        comments = ThreadedComment.objects.filter(content_type=ct, object_pk=id)
        ct = ContentType.objects.get(pk=ct)
        model = ct.model_class()
        obj = model.objects.get(pk=id)
        comment_count = comments.count()
        obj_url = "%s%s/%s/%s" % (self.admin_site.root_path, ct.app_label, ct.model, id)

        if not self.has_delete_permission(request):
            raise PermissionDenied

        if request.POST: # The user has already confirmed the deletion.
            for comment in comments:
                try:
                    comment.delete()
                except ObjectDoesNotExist, e:
                    pass

            from django.contrib.admin.models import LogEntry, CHANGE
            LogEntry.objects.log_action(request.user.id, ct.id, id, force_unicode(obj),
                                        CHANGE, force_unicode(_('Comments deleted')))

            request.user.message_set.create(message=_('The comments were deleted successfully.').__unicode__())
            return HttpResponseRedirect(obj_url)

        context = {
            "title": _("Are you sure?"),
            "ct": ct,
            "model_name": model._meta.verbose_name,
            "obj": obj,
            "app_label": model._meta.app_label,
            'root_path': self.admin_site.root_path,
            "comment_count": comment_count,
            "no_comments": comment_count == 0,
        }
        return render_to_response("admin/comments/comment/multiple_delete_confirmation.html", context)

class BannedIPAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_display = ('__unicode__', 'created', 'reason')
    list_filter = ('created',)

admin.site.register(BannedIP, BannedIPAdmin)
