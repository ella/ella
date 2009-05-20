from django.utils.translation import ugettext_lazy as _, ugettext
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from ella import newman

from ella.galleries.models import Gallery, GalleryItem
from ella.core.newman_admin import PlacementInlineAdmin, PublishableAdmin
from ella.core.cache import get_cached_object

class GalleryItemFormset(newman.options.BaseInlineFormSet):
    " Override default FormSet to allow for custom validation."

    def clean(self):
        """Checks if all objects exist and searches for duplicate references to the same object in one gallery."""
        if not self.is_valid():
            return

        obj = self.instance
        items = set([])

        for i,d in ((i,d) for i,d in enumerate(self.cleaned_data) if d):
            # TODO: why cleaned data does not have target_ct_id prop?
            target = (d['target_ct'].id, d['target_id'],)
            # check if object exists
            try:
                # TODO: wouldn't it be better not to take objects from cache?
                obj = get_cached_object(get_cached_object(ContentType, pk=d['target_ct'].id), pk=d['target_id'])
            except ObjectDoesNotExist:
                raise forms.ValidationError, ugettext('%s with id %i does not exist') % (d['target_ct'], d['target_id'])
            # check for duplicities
            if target in items:
                raise forms.ValidationError, ugettext('There are two references to %s in this gallery') % obj
            items.add(target)

        return self.cleaned_data

class GalleryItemInline(newman.NewmanTabularInline):
    model = GalleryItem
    extra = 10
    formset = GalleryItemFormset

class GalleryAdmin(PublishableAdmin):
    ordering = ('-created',)
    fieldsets = (
        (_("Gallery heading"), {'fields': ('title', 'slug',)}),
        (_("Gallery metadata"), {'fields': ('description', 'content', 'authors', 'category')}),
)
    list_filter = ('created', 'category',)
    search_fields = ('title', 'description', 'slug',)
    inlines = [GalleryItemInline, PlacementInlineAdmin]
    rich_text_fields = {None: ('description', 'content',)}
    prepopulated_fields = {'slug': ('title',)}

newman.site.register(Gallery, GalleryAdmin)

