from django.contrib import admin
from django.http import HttpResponseRedirect
from ella.core.admin import PlacementInlineAdmin
from ella.core.cache.utils import delete_cached_object
from ella.discussions.models import TopicThread, Topic, BannedUser, BannedString
from ella.discussions.cache import get_key_comments_on_thread__spec_filter, get_key_comments_on_thread__by_submit_date
from django.utils.translation import ugettext_lazy as _
from ella.ellaadmin.options import EllaAdminOptionsMixin, EllaModelAdmin

class PostOptions(EllaAdminOptionsMixin, admin.ModelAdmin):
    ordering = ('-submit_date',)
    list_display = ('content', 'submit_date', 'target', 'author', 'is_public', 'path',)
    search_fields = ('subject', 'content', 'id',)
    raw_id_fields = ('parent',)
    fieldsets = (
        (_("Deletion"), {'fields': ('is_public',)}),
        (_("Data"), {
            'fields': (
                    'submit_date',
                    'content',
                    'target_id',
                    'target_ct', # TODO udelat omezujici widget/field - povolit jen TopicThread c.t.
                    'parent',
                    'user',
                    'ip_address',
                    )
            }
        ),
    )

    def __call__(self, request, url):
        if 'memorize_referer' in request.GET and 'HTTP_REFERER' in request.META:
            if 'admin_redirect_after_change' not in request.session:
                request.session['admin_redirect_after_change'] = request.META['HTTP_REFERER']
        return super(PostOptions, self).__call__(request, url)

    def queryset(self, request):
        """ return only Comments which are related to discussion threads. """
        from django.contrib.contenttypes.models import ContentType
        qset = super(PostOptions, self).queryset(request)
        ctThread = ContentType.objects.get_for_model(TopicThread)
        return qset.filter(target_ct=ctThread)

    def save_change(self, request, model, form, formsets=None):
        """ custom redirection back to thread page on portal """
        out = super(PostOptions, self).save_change(request, model, form, formsets)
        if isinstance(out, HttpResponseRedirect) and 'admin_redirect_after_change' in request.session:
            out = HttpResponseRedirect(request.session['admin_redirect_after_change'])
            del request.session['admin_redirect_after_change']
        thr = form.instance.target
        if isinstance(thr, TopicThread): # invalidate cached thread posts
            delete_cached_object(get_key_comments_on_thread__spec_filter(None, thr))
            delete_cached_object(get_key_comments_on_thread__by_submit_date(None, thr))
        return out

class TopicThreadOptions(EllaAdminOptionsMixin, admin.ModelAdmin):
    list_display = ('title', 'topic', 'created', 'author',)
    search_fields = ('title', 'author', 'id',)
    prepopulated_fields = {'slug': ('title',)}

class TopicOptions(EllaAdminOptionsMixin, EllaModelAdmin):
    raw_id_fields = ('photo',)
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'photo_thumb', 'created', 'pk',)
    list_filter = ('category', 'created',)
    inlines = (PlacementInlineAdmin,)
    # rich_text_fields = {None: ('perex',)}
    rich_text_fields = {None: ('description',)}

admin.site.register(Topic, TopicOptions)
admin.site.register(TopicThread, TopicThreadOptions)
admin.site.register([BannedString, BannedUser])

