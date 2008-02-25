from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.db import connection

from tagging.models import TaggingInlineOptions

from ella.core.models import Listing
from ella.core.admin import ListingInlineOptions, HitCountInlineOptions
from ella.ellaadmin import fields
from ella.articles.models import ArticleContents, Article, InfoBox


class ArticleContentInlineOptions(admin.TabularInline):
    model = ArticleContents
    extra = 1
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'content':
            if db_field.blank:
                kwargs['required'] = False
            return fields.RichTextAreaField(**kwargs)
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)

class InfoBoxOptions(admin.ModelAdmin):
    list_display = ('title', 'created',)
    date_hierarchy = 'created'
    list_filter = ('created', 'updated',)
    search_fields = ('title', 'content',)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'content':
            if db_field.blank:
                kwargs['required'] = False
            return fields.RichTextAreaField(**kwargs)
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)




class ArticleOptions(admin.ModelAdmin):
    list_display = ('title', 'category', 'photo_thumbnail', 'created', 'article_age', 'get_hits', 'full_url',)
    date_hierarchy = 'created'
    ordering = ('-created',)
    fieldsets = (
        (_("Article heading"), {'fields': ('title', 'upper_title', 'updated', 'slug')}),
        (_("Article contents"), {'fields': ('perex',)}),
        (_("Metadata"), {'fields': ('category', 'authors', 'source', 'photo')}),
)
    raw_id_fields = ('photo',)
    list_filter = ('category__site', 'created', 'category', 'authors',)
    search_fields = ('title', 'upper_title', 'perex', 'slug',)
    inlines = (ArticleContentInlineOptions, ListingInlineOptions, TaggingInlineOptions,)
    prepopulated_fields = {'slug' : ('title',)}

    #def queryset(self, request):
    #    """
    #    Add listing to the query and sort on publish_from.
    #    """
    #    #FIXME: will omit articles without listing (outer join takes 1:30 to finish)
    #    #TODO: verigy if the sorting isn't overriden in ChangeList - FIXME - it is

    #    # prepare lookup for ArticleOptions.queryset()
    #    qn = connection.ops.quote_name
    #    where_lookup = (
    #            '%s.target_ct_id = %d' % (qn(Listing._meta.db_table),ContentType.objects.get_for_model(Article).id),
    #            '%s.target_id = %s.id' % (qn(Listing._meta.db_table), qn(Article._meta.db_table)),
    #            '%s.category_id = %s.category_id' % (qn(Listing._meta.db_table), qn(Article._meta.db_table)),
    #)

    #    qset = super(ArticleOptions, self).queryset(request)
    #    qset = qset.extra(
    #            tables=[ Listing._meta.db_table, ],
    #            where=where_lookup,
    #            select={'publish_from' : '%s.publish_from' % qn(Listing._meta.db_table),},
    #).order_by('-publish_from')
    #    return qset


    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'perex':
            return fields.RichTextAreaField(**kwargs)
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)

admin.site.register(InfoBox, InfoBoxOptions)
admin.site.register(Article, ArticleOptions)

