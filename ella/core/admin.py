from app_data.admin import AppDataModelAdmin
from django.contrib import admin
from django.forms import models as modelforms

from ella.core.models import Author, Source, Category, Listing, Related


class ListingForm(modelforms.ModelForm):
    class Meta:
        model = Listing


class ListingInlineAdmin(admin.TabularInline):
    model = Listing
    extra = 2
    fieldsets = ((None, {'fields': ('category', 'publish_from', 'publish_to', 'commercial',)}),)


class RelatedInlineAdmin(admin.TabularInline):
    model = Related
    extra = 3
#    raw_id_fields = ('publishable_id',)


class CategoryAdmin(AppDataModelAdmin):
    list_filter = ('site',)
    list_display = ('draw_title', 'tree_path', '__unicode__')
    search_fields = ('title', 'slug',)
    #ordering = ('site', 'tree_path',)
    prepopulated_fields = {'slug': ('title',)}
    declared_fieldsets = ((None, {'fields': ('title', 'slug',
                                             ('description', 'content'),
                                             'template', ('site', 'tree_parent'),
                                             'ella.paginate_by',
                                             'ella.first_page_count',
                                             'ella.propagate_listings')}),)


class AuthorAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    raw_id_fields = ('photo',)


class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url',)
    search_fields = ('name',)


class PublishableAdmin(AppDataModelAdmin):
    """ Default admin options for all publishables """

    list_display = ('title', 'category', 'publish_from')
    list_filter = ('category', 'authors',)
    search_fields = ('title', 'description', 'slug', 'authors__name', 'authors__slug',) # FIXME: 'tags__tag__name',)
    raw_id_fields = ('photo',)
    prepopulated_fields = {'slug': ('title',)}
    rich_text_fields = {None: ('description',)}

    suggest_fields = {
        'category': ('tree_path', 'title', 'slug',),
        'authors': ('name', 'slug', 'email',),
        'source': ('name', 'url',),
    }


class ListingAdmin(admin.ModelAdmin):
    date_hierarchy = 'publish_from'
    list_display = ('__unicode__', 'publish_from', 'publish_to',)
    list_filter = ('category',)
    search_fields = ('publishable__title', 'publishable__slug',
                     'publishable__description',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Listing, ListingAdmin)
