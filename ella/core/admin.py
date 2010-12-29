from django.contrib import admin
from django.forms import models as modelforms

from ella.ellaadmin import widgets
from ella.core.models import Author, Source, Category, Listing, HitCount, Placement
from ella.core.newman_admin import PlacementForm

class PlacementInlineAdmin(admin.TabularInline):
    exclude = ('slug',)
    # template = 'newman/edit_inline/placement.html'
    template = 'admin/edit_inline/placement.html'
    model = Placement
    max_num = 1
    suggest_fields = {'category': ('__unicode__', 'title', 'slug',)}

    form = PlacementForm
    #formset = PlacementInlineFormset

"""
class PlacementInlineAdmin(admin.TabularInline):
    model = Placement
    max_num = 1
    #formset = PlacementInlineFormset
    form = PlacementForm
    extra = 1
    '''
    extra = 1
    ct_field = 'target_ct'
    ct_fk_field = 'target_id'
    formset = PlacementInlineFormset
    form = PlacementForm
    fieldsets = ((None, {'fields' : ('category', 'publish_from', 'publish_to', 'slug', 'static', 'listings',)}),)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'category':
            kwargs['widget'] = widgets.ListingCategoryWidget
        return super(PlacementInlineOptions, self).formfield_for_dbfield(db_field, **kwargs)
    '''
"""


class ListingForm(modelforms.ModelForm):
    class Meta:
        model = Listing

class ListingInlineAdmin(admin.TabularInline):
    model = Listing
    extra = 2
    fieldsets = ((None, {'fields' : ('category','publish_from', 'priority_from', 'priority_to', 'priority_value', 'commercial',)}),)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'category':
            kwargs['widget'] = widgets.ListingCategoryWidget
        return super(ListingInlineAdmin, self).formfield_for_dbfield(db_field, **kwargs)


class HitCountInlineAdmin(admin.TabularInline):
    model = HitCount
    extra = 0

class PlacementAdmin(admin.ModelAdmin):
    pass
    '''
    list_display = ('target_admin', 'category', 'publish_from', 'full_url',)
    list_filter = ('publish_from', 'category', 'target_ct',)
    inlines = (ListingInlineOptions,)
    fieldsets = (
        (_('target'), {'fields': ('target_ct', 'target_id', 'slug', 'category',), 'classes': ('wide',)},),
        (_('time'), {'fields': ('publish_from','publish_to', 'static',), 'classes': ('wide',)},),
    )
    '''

class ListingAdmin(admin.ModelAdmin):
    pass
    '''
    list_display = ('target_admin', 'target_ct', 'publish_from', 'category', 'placement_admin', 'target_hitcounts', 'target_url',)
    list_display_links = ()
    list_filter = ('publish_from', 'category__site', 'category', 'placement__target_ct',)
    raw_id_fields = ('placement',)
    date_hierarchy = 'publish_from'
    '''

class CategoryAdmin(admin.ModelAdmin):
    list_filter = ('site',)
    list_display = ('draw_title', 'tree_path', '__unicode__')
    search_fields = ('title', 'slug',)
    #ordering = ('site', 'tree_path',)
    prepopulated_fields = {'slug': ('title',)}

class HitCountAdmin(admin.ModelAdmin):
    list_display = ('target', 'hits',)
    ordering = ('-hits', '-last_seen',)

class AuthorAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url',)
    search_fields = ('name',)

class PublishableAdmin(admin.ModelAdmin):
    """ Default admin options for all publishables """

    list_display = ('title', 'category',)
    list_filter = ('category', 'authors',)
    search_fields = ('title', 'description', 'slug', 'authors__name', 'authors__slug',) # FIXME: 'tags__tag__name',)
    raw_id_fields = ('photo',)
    prepopulated_fields = {'slug' : ('title',)}
    rich_text_fields = {None: ('description',)}

    suggest_fields = {
        'category': ('tree_path', 'title', 'slug',),
        'authors': ('name', 'slug', 'email',),
        'source': ('name', 'url',),
    }

    #inlines = [PlacementInlineAdmin]


admin.site.register(HitCount, HitCountAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Placement, PlacementAdmin)
admin.site.register(Listing, ListingAdmin)
