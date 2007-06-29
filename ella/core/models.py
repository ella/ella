import string
from datetime import datetime, timedelta
from django.db import models, transaction
from django.contrib import admin
#from django.contrib.admin import site, ModelAdmin, StackedInline, TabularInline
from django.utils.timesince import timesince
from django import newforms as forms
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

DEFAULT_LISTING_PRIORITY = getattr(settings, 'DEFAULT_LISTING_PRIORITY', 0)

class Author(models.Model):
    name = models.CharField(maxlength=200)
    photo = models.ImageField(upload_to='photos/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True)
    text = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering=('name',)

class Source(models.Model):
    name = models.CharField(maxlength=200)
    url = models.URLField(blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    title = models.CharField(maxlength=200, verbose_name=_("Category Title"))
    slug = models.SlugField()
    tree_parent = models.ForeignKey('self', null=True, blank=True, verbose_name=_("Parent Category"))
    #tree_path = models.CharField(maxlength=255, editable=False)
    tree_path = models.CharField(maxlength=255, blank=True)
    description = models.TextField(blank=True, verbose_name=_("Category Description"))

    @transaction.commit_on_success
    def save(self):
        old_tree_path = self.tree_path[:]
        if self.tree_parent:
            self.tree_path = '%s/%s' % (self.tree_parent.tree_path, self.slug)
        else:
            self.tree_path = '/%s' % self.slug
        super(Category, self).save()
        if(old_tree_path != self.tree_path):
            children = Category.objects.filter(tree_path__startswith=old_tree_path)
            for child in children:
                child.tree_path = string.replace(child.tree_path, old_tree_path, self.tree_path)
                child.save()

    @transaction.commit_on_success
    def delete(self):
        children = Category.objects.filter(tree_path_startswith = self.tree_path)
        super(Categry, self).delete()
        for child in chilldren:
            child.delete()

    def draw_title(self):
        return ('&nbsp;&nbsp;' * string.count(self.tree_path, '/', 1)) + self.title
    draw_title.allow_tags = True

    class Meta:
        ordering = ('tree_path', 'title')
        verbose_name = _('Cateory')
        verbose_name_plural = _('Cateories')

    def __str__(self):
        return self.title

class ListingManager(models.Manager):
    NONE = 0
    IMMEDIATE = 1
    ALL = 2
    def clean_listings(self):
        """
        Method that cleans the Listing model by deleting all listings that are no longer valid.
        Should be run periodicaly to purge the DB from unneeded data.
        """
        self.filter(remove=True, priority_to__lte=datetime.now()).delete()

    def _get_queryset(self, category=None, children=NONE, mods=[]):
        now = datetime.now()
        qset = self.exclude(remove=True, priority_to__lte=datetime.now()).filter(publish_from__lte=now)

        if category:
            if children == self.NONE:
                # only this one category
                qset = qset.filter(category=category)
            elif children == self.IMMEDIATE:
                # this category and its children
                qset = qset.filter(models.Q(category__tree_parent=category) | models.Q(category=category))
            else:
                # this category and all its descendants
                qset = qset.filter(category__tree_path__startswith=category.tree_path)

        # filtering based on Model classes
        if mods:
            qset = qset.filter(target_ct__in=[ ContentType.objects.get_for_model(m) for m in mods ])

        return qset

    def get_count(self, category=None, children=NONE, mods=[]):
        return self._get_queryset(category, children, mods).count()

    def get_listing(self, category=None, count=10, offset=1, children=NONE, mods=[]):
        """
        Get top objects for given category and potentionally also its child categories.

        Params:
            category - Category object to list objects for. None if any category will do
            count - number of objects to output, defaults to 10
            offset - starting with object number... 1-based
            children - one of
                            NONE: only this category
                            IMMEDIATE: this category and its immediate children
                            ALL: all descendants from the given category
            mods - list of Models, if empty, object from all models are included
        """
        now = datetime.now()
        qset = self._get_queryset(category, children, mods).select_related()

        # listings with active priority override
        active = models.Q(priority_from__lte=now, priority_to__gte=now)

        qsets = (
            # modded-up objects
            qset.filter(active, priority_value__gt=DEFAULT_LISTING_PRIORITY).order_by('-priority_value', '-publish_from'),
            # default priority
            qset.exclude(active).order_by('-publish_from'),
            # modded-down priority
            qset.filter(active, priority_value__lt=DEFAULT_LISTING_PRIORITY).order_by('-priority_value', '-publish_from'),
)

        out = []

        if offset > 0:
            offset -=1

        # iterate through qsets until we have enough objects
        for q in qsets:
            data = q[offset:offset+count]
            if data:
                offset = 0
                out.extend(data)
                count -= len(data)
                if count <= 0:
                    break
            else:
                offset -= q.count()
        return out

class Listing(models.Model):
    target_ct = models.ForeignKey(ContentType)
    target_id = models.IntegerField()

    target = generic.GenericForeignKey('target_ct', 'target_id')

    category = models.ForeignKey(Category, db_index=True)

    publish_from = models.DateTimeField(_("Start of listing"), default=datetime.now)
    priority_from = models.DateTimeField(_("Start of prioritized listing"), default=datetime.now, null=True, blank=True)
    priority_to = models.DateTimeField(_("End of prioritized listing"), default=lambda: datetime.now() + timedelta(days=7), null=True, blank=True)
    priority_value = models.IntegerField(_("Priority"))
    remove = models.BooleanField(_("Remove"), help_text=_("Remove object from listing after the priority wears off?"), default=False)

    objects = ListingManager()

    def save(self):
        # do not allow prioritizations without priority_value
        if self.priority_value == DEFAULT_LISTING_PRIORITY:
            self.priority_from = None
        super(Listing, self).save()

    def _get_priority(self):
        """
        Get the actual priority according to settings.
        """
        now = datetime.now()
        if now > self.priority_to and self.remove:
            return None
        elif self.priority_from <= now <= self.priority_to:
            return self.priority_value
        else:
            return DEFAULT_LISTING_PRIORITY
    priority = property(_get_priority)

    class Meta:
        verbose_name = _('Listing')
        verbose_name_plural = _('Listings')

class Dependency(models.Model):
    target_ct = models.ForeignKey(ContentType, related_name='dependency_for_set')
    target_id = models.IntegerField()

    target = generic.GenericForeignKey('target_ct', 'target_id')

    source_ct = models.ForeignKey(ContentType, related_name='dependent_on_set')
    source_id = models.IntegerField()

    source = generic.GenericForeignKey('source_ct', 'source_id')

    class Meta:
        verbose_name = _('Dependency')
        verbose_name_plural = _('Dependencies')
        ordering = ('source_ct', 'source_id',)

import widgets
class ListingOptions(admin.ModelAdmin):
    raw_id_fields = ('target_id',)
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ('target_ct',):
            return forms.ModelChoiceField(
                        queryset=ContentType.objects.all(),
                        widget=widgets.ContentTypeWidget(db_field.name.replace('_ct', '_id')),
)
        elif db_field.name == 'target_id':
            return super(ListingOptions, self).formfield_for_dbfield(db_field, widget=widgets.ForeignKeyRawIdWidget , **kwargs)

        return super(ListingOptions, self).formfield_for_dbfield(db_field, **kwargs)

class DependencyOptions(admin.ModelAdmin):
    raw_id_fields = ('target_id', 'source_id')

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ('target_ct', 'source_ct'):
            return forms.ModelChoiceField(
                        queryset=ContentType.objects.all(),
                        widget=widgets.ContentTypeWidget(db_field.name.replace('_ct', '_id')),
)
        elif db_field.name in ('target_id', 'source_id'):
            return super(DependencyOptions, self).formfield_for_dbfield(db_field, widget=widgets.ForeignKeyRawIdWidget , **kwargs)

        return super(DependencyOptions, self).formfield_for_dbfield(db_field, **kwargs)

class CategoryOption(admin.ModelAdmin):
    list_display = ('draw_title', 'tree_path')
    ordering = ('tree_path',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = []

class AuthorOptions(admin.ModelAdmin):
    inlines = []

admin.site.register(Category, CategoryOption)
admin.site.register(Source)
admin.site.register(Author, AuthorOptions)
admin.site.register(Listing, ListingOptions)
admin.site.register(Dependency , DependencyOptions)

