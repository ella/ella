from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.contrib import admin
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from ella.core.models import Listing, Category
from ella.core.cache import get_cached_object
from ella.photos.models import Photo
from django.template.defaultfilters import slugify

class Topic(models.Model):
    # ella fields
    slug = models.CharField(_('Slug'), db_index=True, maxlength=255)
    category = models.ForeignKey(Category, verbose_name=_('Category'))

    photo = models.ForeignKey(Photo, blank=True, null=True, verbose_name=_('Photo'))
    created = models.DateTimeField(_('Created'), default=datetime.now, editable=False)

    title = models.CharField(_('Title'), maxlength=255)
    description = models.TextField(_('Description'))

    def __unicode__(self):
        return self.title

    @property
    def main_listing(self):
        try:
            return get_cached_object(
                    Listing,
                    target_ct=ContentType.objects.get_for_model(self.__class__),
                    target_id=self.id,
                    category=self.category_id
)
        except Listing.DoesNotExist:
            return None

    def get_absolute_url(self):
        listing = self.main_listing
        if listing:
            return listing.get_absolute_url()

class Question(models.Model):
    topic = models.ForeignKey(Topic)
    slug = models.CharField(_('Slug'), db_index=True, maxlength=255)

    title = models.CharField(_('Title'), maxlength=255)
    description = models.TextField(_('Description'))

    # author if is authorized
    user = models.ForeignKey(User, verbose_name=_('authorized author'), blank=True, null=True)
    # author otherwise
    nickname = models.CharField(_("anonymous author's nickname"), maxlength=255, blank=True)
    email = models.EmailField(_('authors email (optional)'), blank=True)

    # authors ip address
    ip_address = models.IPAddressField(_('ip address'), blank=True, null=True)

    created = models.DateTimeField(_('Created'), default=datetime.now, editable=False)
    is_public = models.BooleanField(_('is public'), default=True)

    def get_absolute_url(self):
        top = get_cached_object(Topic, pk=self.topic_id)
        return '%s%s/%s/' % (top.get_absolute_url(), slugify(ugettext('question')), self.slug)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')
        unique_together = (('topic', 'slug',),)
        ordering = ('-created',)

class QuestionOptions(admin.ModelAdmin):
    pass

class TopicOptions(admin.ModelAdmin):
    raw_id_fields = ('photo',)
    def formfield_for_dbfield(self, db_field, **kwargs):
        from ella.core.admin import widgets
        from django import newforms as forms
        if db_field.name == 'perex':
            kwargs['widget'] = widgets.RichTextAreaWidget
        if db_field.name == 'slug':
            return forms.RegexField('^[0-9a-z-]+$', max_length=255, **kwargs)
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)

admin.site.register(Question, QuestionOptions)
admin.site.register(Topic, TopicOptions)

from ella.core.custom_urls import dispatcher

def question(request, bits, context):
    from ella.discussions.views import question as real_func
    return real_func(request, bits, context)
def ask_question(request, bits, context):
    from ella.discussions.views import ask_question as real_func
    return real_func(request, bits, context)

def topic(request, context):
    from ella.discussions.views import topic as real_func
    return real_func(request, context)

dispatcher.register(_('ask'), ask_question, model=Topic)
dispatcher.register(_('question'), question, model=Topic)
dispatcher.register_custom_detail(Topic, topic)
