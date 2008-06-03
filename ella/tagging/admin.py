from django.contrib import admin
from django.contrib.contenttypes import generic
from django.newforms import models as modelforms
from django.newforms import model_to_dict
from django import newforms as forms
from ella.tagging.models import Tag, TaggedItem
from django.utils.translation import ugettext_lazy as _
from ella.tagging.fields import SuggestTagAdminField, TagPriorityAdminField
from django.contrib.contenttypes.models import ContentType

class TagInlineForm(modelforms.ModelForm):
    class Meta:
        model = TaggedItem

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)


class TagInlineFormset(modelforms.BaseModelFormSet):
    def __init__(self, data=None, files=None, instance=None):
        # instance ... <Article: neco>
        # self.extra_forms, self.initial_forms ... formulare formsetu
        self.queryset = None
        self.instance = instance
        tags_by_prio = {}
        initial = []
        if instance:
            qs = TaggedItem.objects.get_for_object(instance)
            for ti in qs:
                if not ti.priority in tags_by_prio:
                    tags_by_prio[ ti.priority ] = []
                tags_by_prio[ ti.priority ].append(ti.tag)
            for k, v in tags_by_prio.items():
                initial.append({'priority': k, 'tag': v})
        super(modelforms.BaseModelFormSet, self).__init__(
            data=data,
            files=files,
            prefix='tagged_item_',
            initial=initial
)

    def save_existing(self, form, instance, commit=True):
        instance = super(self.__class__, self).save_existing(form, instance, commit)
        # mmj. se vola instance._meta.fields[ n ].save_form_data(instance, cleaned_data[f.name])
        import pdb;pdb.set_trace()
        return instance

    def save_new(self, form, commit=True):
        instance = super(self.__class__, self).save_new(form, commit)
        import pdb;pdb.set_trace()
        return instance

    def save(self):
        # self.initial
        import pdb;pdb.set_trace()
        for d in self.cleaned_data:
            d['priority']
            d['tags']


    """
    def get_queryset(self):
        if self.queryset:
            return self.queryset
        return self.model._default_manager.get_queryset()

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
        instance = super(self.__class__, self).save_existing(form, instance, commit)
        self.__add_category(form, instance, commit)
        return instance

    def save_new(self, form, commit=True):
        instance = super(self.__class__, self).save_new(form, commit)
        self.__add_category(form, self.instance, commit)
        return instance
    """


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
