from django.contrib import admin
from django.contrib.contenttypes import generic
from django.newforms import models as modelforms
from ella.tagging.models import Tag, TaggedItem
from django.utils.translation import ugettext_lazy as _
from ella.tagging.fields import SuggestTagAdminField, TagPriorityAdminField
from django.contrib.contenttypes.models import ContentType

class TagInlineFormset(generic.GenericInlineFormset):

    def __add_category(self, form, instance, commit):
        if not commit:
            return
        if not hasattr(instance, 'category'):
            return
        # kategorii ziskam: [self.]instance.object.category
        # v teto chvili je ulozeny TaggedItem ok, ale s prazdnym polem "category"
        # self.get_queryset() vrati QSet instanci TaggedItem
        # form.cleaned_data obsahuje slovnik atributu ukladaneho: {'tag': <Tag: kremenac>, 'id': None}
        if isinstance(instance, TaggedItem):
            obj = instance.object
        else:
            obj = instance
        tag = form.cleaned_data['tag']
        ct = ContentType.objects.get_for_model(type(obj)) # tagged object ContentType
        ti = TaggedItem.objects.get(
            content_type=ct,
            object_id=obj._get_pk_val(),
            tag=tag
)
        ti.category = obj.category
        ti.save()

    def save_existing(self, form, instance, commit=True):
        instance = super(TagInlineFormset, self).save_existing(form, instance, commit)
        self.__add_category(form, instance, commit)
        return instance

    def save_new(self, form, commit=True):
        instance = super(TagInlineFormset, self).save_new(form, commit)
        self.__add_category(form, self.instance, commit)
        return instance

class TaggingInlineOptionsSimple(admin.TabularInline):
    model = TaggedItem
    extra = 0

class TaggingInlineOptions(generic.GenericTabularInline):
    fields = ('tag', 'priority',)
    raw_id_fields = ('tag',)
    model = TaggedItem
    extra = 4
    id_field_name = 'object_id'
    ct_field_name = 'content_type'
    formset = TagInlineFormset

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'tag':
            return SuggestTagAdminField(db_field, **kwargs)
        elif db_field.name == 'priority':
            return TagPriorityAdminField(db_field, **kwargs)
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


