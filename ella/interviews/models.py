from datetime import datetime

from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from ella.ellaadmin import widgets
from ella.photos.models import Photo
from ella.core.managers import RelatedManager
from ella.core.admin.models import ListingInlineOptions
from ella.core.cache import get_cached_object, get_cached_list
from ella.core.models import Listing, Category, Author, Source

class Interviewee(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    author = models.ForeignKey(Author, null=True, blank=True)
    name = models.CharField(_('Name'), maxlength=200, blank=True)
    slug = models.CharField(_('Slug'), maxlength=200)
    description = models.TextField(_('Description'), blank=True)

    class Meta:
        verbose_name = _('Interviewee')
        verbose_name_plural = _('Interviewees')
        ordering = ('name',)

    def __unicode__(self):
        if self.author_id:
            return unicode(get_cached_object(Author, pk=self.author_id))
        elif self.user_id:
            return unicode(get_cached_object(User, pk=self.user_id))
        return self.name


class Interview(models.Model):
    # Titles
    title = models.CharField(_('Title'), maxlength=255)
    upper_title = models.CharField(_('Upper title'), maxlength=255, blank=True)
    slug = models.CharField(_('Slug'), db_index=True, maxlength=255)

    # Contents
    perex = models.TextField(_('Perex'))
    active_from = models.DateTimeField(_('Active from'))
    active_to = models.DateTimeField(_('Active to'))

    # Authors and Sources
    authors = models.ManyToManyField(Author, verbose_name=_('Authors'))
    source = models.ForeignKey(Source, blank=True, null=True, verbose_name=_('Source'))
    interviewees = models.ManyToManyField(Interviewee, verbose_name=_('Interviewees'))

    category = models.ForeignKey(Category, verbose_name=_('Category'))

    # Main Photo
    photo = models.ForeignKey(Photo, blank=True, null=True, verbose_name=_('Photo'))

    objects = RelatedManager()

    @property
    def active(self):
        now = datetime.now()
        return self.active_from <= now < active_to

    def get_interviewees(self, request):
        if not self.active or not request.user.is_authenticated():
            return []

        interviewees = get_cached_list(Interviewee, interview__pk=self.pk)
        # TODO: filter only those interviewees that can be replying now (permission-wise)
        return interviewees

    def get_photo(self):
        if not hasattr(self, '_photo'):
            try:
                self._photo = get_cached_object(Photo, pk=self.photo_id)
            except Photo.DoesNotExist:
                self._photo = None
        return self._photo

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

    def full_url(self):
        absolute_url = self.get_absolute_url()
        if absolute_url:
            return '<a href="%s">url</a>' % absolute_url
        return 'no url'
    full_url.allow_tags = True


    class Meta:
        verbose_name = _('Interview')
        verbose_name_plural = _('Interviews')
        ordering = ('-active_from',)

    def __unicode__(self):
        return self.title


class IntervieweeOptions(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'author',)
    search_fields = ('user__first_name', 'user__last_name', 'name', 'description', 'slug', 'author__name',)
    prepopulated_fields = {'slug' : ('name',)}

class InterviewOptions(admin.ModelAdmin):
    list_display = ('title', 'category', 'active_from', 'full_url',)
    list_filter = ('category__site', 'active_from', 'category', 'authors',)
    date_hierarchy = 'active_from'
    raw_id_fields = ('photo', 'interviewees',)
    search_fields = ('title', 'perex',)
    prepopulated_fields = {'slug' : ('title',)}
    inlines = (ListingInlineOptions,)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'perex':
            kwargs['widget'] = widgets.RichTextAreaWidget
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)

admin.site.register(Interviewee, IntervieweeOptions)
admin.site.register(Interview, InterviewOptions)
