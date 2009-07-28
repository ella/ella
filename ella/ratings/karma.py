from django.core.exceptions import ImproperlyConfigured
from django.db.models.fields import FieldDoesNotExist
from django.contrib.auth.models import SiteProfileNotAvailable

from ella.ratings.models import *

try:
    profile_model = models.get_model(*settings.AUTH_PROFILE_MODULE.split('.'))
except (ImportError, ImproperlyConfigured, AttributeError):
    profile_model = None


UPDATE_STATEMENT_MYSQL_AGG = '''
    UPDATE
        %(profile_table)s,
        (
            SELECT
                obj_tab.%(owner_field)s AS owner_id,
                SUM(aggregation.amount) * %(weight)s AS amount,
                COUNT(*) AS cnt
            FROM
                 %(aggreg_table)s aggregation JOIN %(obj_table)s obj_tab ON (aggregation.target_id = obj_tab.%(obj_pk)s)
            WHERE
                aggregation.target_ct_id = %%(ct_type)s
            GROUP BY
                obj_tab.%(owner_field)s
) AS agg
    SET
        karma = karma + (%(karma_coeficient)s * agg.amount)
    WHERE
        %(profile_table)s.user_id = agg.owner_id;
'''

UPDATE_STATEMENT_MYSQL_RATE = '''
    UPDATE
        %(profile_table)s,
        (
            SELECT
                obj_tab.%(owner_field)s AS owner_id,
                SUM(ratings.amount * %(rating_coeficient)s)* %(weight)s AS amount,
                COUNT(*) AS cnt
            FROM
                %(rating_table)s ratings JOIN %(obj_table)s obj_tab ON (ratings.target_id = obj_tab.%(obj_pk)s)
            WHERE
                ratings.target_ct_id = %%(ct_type)s
            GROUP BY
                obj_tab.%(owner_field)s
) AS rate
    SET
        karma = karma + (%(karma_coeficient)s * rate.amount)
    WHERE
        %(profile_table)s.user_id = rate.owner_id;
'''


if settings.DATABASE_ENGINE == 'mysql':
    UPDATE_STATEMENT_AGG = UPDATE_STATEMENT_MYSQL_AGG
    UPDATE_STATEMENT_RATE = UPDATE_STATEMENT_MYSQL_RATE
else:
    raise ImproperlyConfigured, "Use MySQL for karma functionality"

def update_karma_for_ct(content_type, owner_field, weight):
    """
    Function that recalculate karma points for individual content type.
    it works directly in the databse using an UPDATE statement utilizing JOINs,
    PostgreSQL is required for this to work.

    Params:
        content_type: ContentType object refering to the model we are processing
        owner_field: name of the Field identifying the owner of the object
        weight: weight (importance) of the model

    Raises:
        SiteProfileNotAvailable if User model doesn't have an associated profile
    """
    if not profile_model:
        raise SiteProfileNotAvailable
    try:
        karma_coeficient = '%s.%s' % (
                    connection.ops.quote_name(profile_model._meta.db_table),
                    connection.ops.quote_name(profile_model._meta.get_field('karma_coeficient').column)
        )
    except FieldDoesNotExist:
        karma_coeficient = Decimal("1.0")

    sql = UPDATE_STATEMENT_AGG % {
        'weight' : weight,
        'karma_coeficient' : karma_coeficient,
        'profile_table' : connection.ops.quote_name(profile_model._meta.db_table),
        'owner_field' : connection.ops.quote_name(content_type.model_class()._meta.get_field(owner_field).column),
        'aggreg_table' : connection.ops.quote_name(TotalRate._meta.db_table),
        'obj_table' : connection.ops.quote_name(content_type.model_class()._meta.db_table),
        'obj_pk' : connection.ops.quote_name(content_type.model_class()._meta.pk.column),
    }

    cursor = connection.cursor()
    cursor.execute(sql, {'ct_type' : content_type.id,})

    sql = UPDATE_STATEMENT_RATE % {
        'weight' : weight,
        'karma_coeficient' : karma_coeficient,
        'rating_coeficient' : RATINGS_COEFICIENT,
        'profile_table' : connection.ops.quote_name(profile_model._meta.db_table),
        'owner_field' : connection.ops.quote_name(content_type.model_class()._meta.get_field(owner_field).column),
        'rating_table' : connection.ops.quote_name(Rating._meta.db_table),
        'obj_table' : connection.ops.quote_name(content_type.model_class()._meta.db_table),
        'obj_pk' : connection.ops.quote_name(content_type.model_class()._meta.pk.column),
    }

    cursor.execute(sql, {'ct_type' : content_type.id,})



#@transaction.commit_on_success
def recalculate_karma():
    """
    Function that will recalculate users' karmas start to finish.

    Raises:
        SiteProfileNotAvailable if User model doesn't have an associated profile
    """
    if not profile_model:
        raise SiteProfileNotAvailable

    sql = '''
        UPDATE
            %s
        SET
            karma = %%s
    ''' %  connection.ops.quote_name(profile_model._meta.db_table)
    cursor = connection.cursor()
    cursor.execute(sql, (INITIAL_USER_KARMA,))

    for mw in ModelWeight.objects.all():
        update_karma_for_ct(mw.content_type, mw.owner_field, mw.weight)
    return True

if __name__ == '__main__':
    recalculate_karma()

