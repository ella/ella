from datetime import datetime

from django.db import models, backend, connection
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

# ratings - specific settings
ANONYMOUS_KARMA = getattr(settings, 'ANONYMOUS_KARMA', 1)
INITIAL_USER_KARMA = getattr(settings, 'ANONYMOUS_KARMA', 4)
DEFAULT_MODEL_WEIGHT = getattr(settings, 'DEFAULT_MODEL_WEIGHT', 1)
MINIMAL_ANONYMOUS_IP_DELAY = getattr(settings, 'MINIMAL_ANONYMOUS_IP_DELAY', 1800)
RATINGS_COOKIE_NAME = getattr(settings, 'RATINGS_COOKIE_NAME', 'ratings_voted')
RATINGS_MAX_COOKIE_LENGTH = getattr(settings, 'RATINGS_MAX_COOKIE_LENGTH', 20)
RATINGS_MAX_COOKIE_AGE = getattr(settings, 'RATINGS_MAX_COOKIE_AGE', 3600)


MODEL_WEIGHT_CACHE = {}
class ModelWeightManager(models.Manager):
    """
    Manager class that handles one additional method - getweight(model), which will return weight for a given model
    """
    def get_weight(self, model):
        """
        Returns the weight for the given model.

        Params:
            model: model class or instance to work with
        """
        opts = model._meta
        key = (opts.app_label, opts.object_name.lower())

        try:
            weight = MODEL_WEIGHT_CACHE[key]
        except KeyError:
            try:
                mw = self.get(content_type=ContentType.objects.get_for_model(model))
                weight = mw.weight
            except ModelWeight.DoesNotExist:
                weight = DEFAULT_MODEL_WEIGHT

            MODEL_WEIGHT_CACHE[key] = weight

        return weight

    def clear_cache(self):
        """
        Clear out the model-weight cache. This needs to happen during database
        flushes to prevent caching of "stale" model weights IDs (see
        ella.ratings.management.create_model_weights and ModelWeight.save() for where
        this gets called).

        Taken from django.contrib.contenttypes.models, thanks.
        """
        global MODEL_WEIGHT_CACHE
        MODEL_WEIGHT_CACHE = {}


class ModelWeight(models.Model):
    """
    Importance of each Model when it comes to computing owner's Karma.
    """
    content_type = models.OneToOneField(ContentType)
    weight = models.IntegerField(_('Weight'), default=DEFAULT_MODEL_WEIGHT)
    owner_field = models.CharField(_('Owner field'), maxlength=30, help_text=_('Name of the field on target model that identifies the owner of the object'))

    objects = ModelWeightManager()

    def save(self):
        """
        Clear the cache and do the save()
        """
        ModelWeight.objects.clear_cache()
        return super(ModelWeight, self).save()

    class Meta:
        verbose_name = _('Model weight')
        verbose_name_plural = _('Model weights')
        ordering = ('-weight',)

class RatingManager(models.Manager):
    def get_top_objects(self, count, mods=[]):
        """
        Return count objects with the highest rating.

        Params:
            count: number of objects to return
            mods: if specified, limit the result to given model classes
        """
        where = ''
        if mods:
            where = ' WHERE target_ct_id IN (%s) ' % ', '.join('%s' % ContentType.objects.get_for_model(m).id for m in mods)

        sql = '''
            SELECT
                ct.app_label, ct.model, agg.target_id, agg.amount
            FROM
                (
                    SELECT
                        target_ct_id,
                        target_id,
                        SUM(amount) as amount
                    FROM %s
                    %s
                    GROUP BY
                        target_ct_id, target_id
) agg JOIN %s ct on ct.id = agg.target_ct_id
            ORDER BY
                agg.amount DESC
            LIMIT %%s''' % (
                backend.quote_name(Rating._meta.db_table),
                where,
                backend.quote_name(ContentType._meta.db_table),
)
        cursor = connection.cursor()
        cursor.execute(sql, (count,))

        return [ (models.get_model(*row[:2])._default_manager.get(pk=row[2]), row[3]) for row in cursor.fetchall() ]

    def get_for_object(self, obj):
        """
        Return the rating for a given object.

        Params:
            obj: object to work with
        """
        content_type = ContentType.objects.get_for_model(obj)
        sql = 'SELECT SUM(amount) FROM %s WHERE target_id = %s AND target_ct_id = %s' % (
            backend.quote_name(Rating._meta.db_table),
            obj.id,
            content_type.id,
)
        cursor = connection.cursor()
        cursor.execute(sql, ())
        result = cursor.fetchone()
        return result[0] or 0

class Rating(models.Model):
    """
    Rating of an object.
    """
    target_ct = models.ForeignKey(ContentType, db_index=True)
    target_id = models.PositiveIntegerField(_('Object ID'), db_index=True)
    target = generic.GenericForeignKey('target_ct', 'target_id')

    time = models.DateTimeField(_('Time'), default=datetime.now, editable=False)
    user = models.ForeignKey(User, blank=True, null=True)
    amount = models.IntegerField(_('Amount'))
    ip_address = models.CharField(_('IP Address'), maxlength="15", blank=True)

    objects = RatingManager()

    def __unicode__(self):
        return u'%s points for %s' % (self.amount, self.target)

    class Meta:
        verbose_name = _('Rating')
        verbose_name_plural = _('Ratings')
        ordering = ('-time',)

    def save(self):
        """
        Modified save() method that checks for duplicit entries.
        """
        if not self.id:
            # fail silently on inserting duplicate ratings
            if self.user:
                try:
                    Rating.objects.get(target_ct=self.target_ct, target_id=self.target_id, user=self.user)
                    return
                except Rating.DoesNotExist:
                    pass
            elif (self.ip_address and Rating.objects.filter(
                        target_ct=self.target_ct,
                        target_id=self.target_id,
                        user__isnull=True,
                        ip_address=self.ip_address ,
                        tim__gte=(self.time or datetime.now()) - timedelta(seconds=MINIMAL_ANONYMOUS_IP_DELAY)
).count() > 0):
                return

        super(Rating, self).save()

from django.db.models import Q
from django.utils.datastructures import SortedDict

class QLeftOuterJoin(Q):
    """
    Django ORM hack that enables you to specify outer join.
    """
    def __init__(self, alias, table, where):
        self.alias, self.table, self.where = alias, table, where

    def get_sql(self, opts):
        """
        Return the appropriate SQL fragments
        """
        joins = SortedDict()
        joins[self.alias] = (self.table, 'LEFT OUTER JOIN', self.where)
        return (joins, [], [])

class RatedManager(models.Manager):
    def get_query_set(self):
        """
        Overriden method that adds rating field to the queryset
        """
        qset = super(RatedManager, self).get_query_set()
        ct = ContentType.objects.get_for_model(qset.model)
        return qset.filter(
                    QLeftOuterJoin(
                        'rating_agg',
                        '(SELECT target_id, SUM(amount) AS amount FROM ratings_rating WHERE target_ct_id = %d GROUP BY ratings_rating.target_id)' % ct.id,
                        '%s.id = rating_agg.target_id' % backend.quote_name(qset.model._meta.db_table)
)
).extra(select={'rating' : 'COALESCE(rating_agg.amount, 0)'})



from django.contrib import admin

class RatingOptions(admin.ModelAdmin):
    list_filter = ('time', 'target_ct',)
    list_display = ('__unicode__', 'time', 'amount', 'user',)

class ModelWeightOptions(admin.ModelAdmin):
    list_filter = ('content_type',)
    list_display = ('content_type', 'weight', 'owner_field',)

admin.site.register(Rating, RatingOptions)
admin.site.register(ModelWeight, ModelWeightOptions)

