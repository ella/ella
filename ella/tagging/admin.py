from django.contrib import admin
from django.contrib.contenttypes import generic
from django.newforms import models as modelforms
from ella.tagging.models import Tag, TaggedItem
from django.utils.translation import ugettext_lazy as _

class TaggingForm(modelforms.ModelForm):
    class Meta:
        model = TaggedItem

    def __init__(self, *args, **kwargs):
        initial = []
        if 'initial' in kwargs:
            initial = [ c.id for c in Category.objects.distinct().filter(listing__placement=kwargs['initial']['id']) ]

        self.base_fields['listings'] = modelforms.ModelMultipleChoiceField(Category.objects.all(), cache_choices=True, required=False, initial=initial)
        super(PlacementForm, self).__init__(*args, **kwargs)


class PlacementInlineFormset(generic.GenericInlineFormset):
    def save_existing(self, form, instance, commit=True):
        instance = super(PlacementInlineFormset, self).save_existing(form, instance, commit)
        return self.save_listings(form, instance, commit)

    def save_new(self, form, commit=True):
        instance = super(PlacementInlineFormset, self).save_new(form, commit)
        return self.save_listings(form, instance, commit)

    def save_listings(self, form, instance, commit=True):
        list_cats = form.cleaned_data.pop('listings')

        def save_listings():
            listings = dict([ (l.category, l) for l in Listing.objects.filter(placement=instance.pk) ])

            for c in list_cats:
                if not c in listings:
                    # create listing
                    l = Listing(placement=instance, category=c, publish_from=instance.publish_from)
                    l.save()
                else:
                    del listings[c]
            for l in listings.values():
                l.delete()

        if commit:
            save_listings()
        else:
            save_m2m = form.save_m2m
            def save_all():
                save_m2m()
                save_listings()
            form.save_m2m = save_all
        return instance


class TaggingInlineOptionsSimple(admin.TabularInline):
    model = TaggedItem
    extra = 0

class TaggingInlineOptions(generic.GenericTabularInline):
    fields = ('tag',)
    raw_id_fields = ('tag',)
    model = TaggedItem
    extra = 4
    id_field_name = 'object_id'
    ct_field_name = 'content_type'
    formset = TaggingForm

    def formfield_for_dbfield(self, db_field, **kwargs):
        from ella.tagging.fields import SuggestTagAdminField
        if db_field.name == 'tag':
            import pdb;pdb.set_trace()
            if hasattr(self.parent_model, 'category'):
                kwargs['category'] = self.parent_model.category
            return SuggestTagAdminField(db_field, **kwargs)
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)

class TagOptions(admin.ModelAdmin):
    ordernig = ('name',)
    list_display = ('name',)
    inlines = (TaggingInlineOptionsSimple,)
    search_fields = ('name',)

class TaggedItemOptions(admin.ModelAdmin):
    list_display = ('tag', 'content_type',)

admin.site.register(Tag, TagOptions)
admin.site.register(TaggedItem, TaggedItemOptions)


