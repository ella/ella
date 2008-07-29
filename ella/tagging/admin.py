from django.contrib import admin
from django.contrib.contenttypes import generic
from django.forms import models as modelforms
from django.forms import model_to_dict
from django import forms
from ella.tagging.models import Tag, TaggedItem
from django.utils.translation import ugettext_lazy as _
from ella.tagging.fields import SuggestTagAdminField, TagPriorityAdminField
from django.contrib.contenttypes.models import ContentType

class TagInlineForm(modelforms.ModelForm):
    class Meta:
        model = TaggedItem

    def __init__(self, *args, **kwargs):
        super(TagInlineForm, self).__init__(*args, **kwargs)


class TagInlineFormset(modelforms.BaseModelFormSet):
    def __init__(self, data=None, files=None, instance=None, save_as_new=None):
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
            # sort aplhabeticaly
            map(lambda x: x.sort(), tags_by_prio.values())
            for k, v in tags_by_prio.items():
                initial.append({'priority': k, 'tag': v})
        super(modelforms.BaseModelFormSet, self).__init__(
            data=data,
            files=files,
            prefix='tagged_item_',
            initial=initial
)

    def save(self):
        self.new_objects = []
        self.changed_objects = []
        self.deleted_objects = []
        for d in self.cleaned_data:
            if 'priority' not in d or 'tag' not in d:
                continue
            obj = self.instance
            ct = ContentType.objects.get_for_model(obj)
            tis = TaggedItem.objects.filter(
                content_type=ct,
                object_id=obj._get_pk_val(),
                category=obj.category,
                priority=d['priority']
)
            tags_before = set(map(lambda x: x.tag, tis))
            saved_tags = []
            for t in d['tag']:
                if t in saved_tags:
                    continue
                ti, created = Tag.objects.add_tag(obj, t.name, int(d['priority']))
                saved_tags.append(ti.tag)
            st = set(saved_tags)
            if tags_before == st:
                continue
            diff = tags_before - st
            while diff:
                ti = TaggedItem.objects.get(
                    tag=diff.pop(),
                    content_type=ct,
                    object_id=obj._get_pk_val(),
                    category=obj.category,
                    priority=d['priority']
)
                ti.delete()


    """
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
        return super(TaggingInlineOptions, self).formfield_for_dbfield(db_field, **kwargs)

class TagOptions(admin.ModelAdmin):
    ordernig = ('name',)
    list_display = ('name',)
    inlines = (TaggingInlineOptionsSimple,)
    search_fields = ('name',)

class TaggedItemOptions(admin.ModelAdmin):
    list_display = ('tag', 'content_type',)

admin.site.register(Tag, TagOptions)
admin.site.register(TaggedItem, TaggedItemOptions)
