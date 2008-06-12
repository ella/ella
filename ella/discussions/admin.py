from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.newforms.widgets import *
from ella.core.admin import PlacementInlineOptions
from ella.ellaadmin import widgets
from ella.discussions.models import TopicThread, Topic, BannedUser, BannedString, get_comments_on_thread
from ella.comments.models import Comment
from ella.comments.admin import CommentsOptions
from ella.ellaadmin.options import EllaAdminSite
from django.utils.translation import ugettext_lazy as _


class PostOptions(admin.ModelAdmin):
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
}),
)

    def queryset(self, request):
        """ return only Comments which are related to discussion threads. """
        from django.contrib.contenttypes.models import ContentType
        qset = super(self.__class__, self).queryset(request)
        ctThread = ContentType.objects.get_for_model(TopicThread)
        return qset.filter(target_ct=ctThread)

class TopicThreadOptions(admin.ModelAdmin):
    list_display = ('title', 'topic', 'created', 'author',)
    search_fields = ('title', 'author', 'id',)
    prepopulated_fields = {'slug': ('title',)}

class TopicOptions(admin.ModelAdmin):
    raw_id_fields = ('photo',)
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'photo_thumb', 'created',)
    inlines = (PlacementInlineOptions,)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'perex':
            kwargs['widget'] = widgets.RichTextAreaWidget
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)

class MyAdmin(admin.AdminSite):
    pass


discussions_admin = MyAdmin()
discussions_admin.register(Comment, PostOptions)
discussions_admin.register(Topic, TopicOptions)
discussions_admin.register(TopicThread, TopicThreadOptions)
discussions_admin.register(BannedString)
discussions_admin.register(User)
from ella.photos.models import Photo, FormatedPhoto
from ella.photos.admin import PhotoOptions, FormatedPhotoOptions
from djangoapps.registration.models import *
discussions_admin.register(Photo, PhotoOptions)
discussions_admin.register(RegistrationProfile, RegistrationProfileOptions)
#discussions_admin.register(FormatedPhoto, FormatedPhotoOptions)

# threadedcomments are registered automaticaly by their module
admin.site.register(Topic, TopicOptions)
admin.site.register(TopicThread, TopicThreadOptions)
admin.site.register(BannedString)

