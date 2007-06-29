from django.db import backend, models, transaction, connection
from django.db.models.fields import FieldDoesNotExist
from django.conf import settings
from django.contrib.auth.models import SiteProfileNotAvailable

from ella.ratings.models import *

try:
    profile_model = models.get_model(*settings.AUTH_PROFILE_MODULE.split('.'))
except (ImportError, ImproperlyConfigured, AttributeError):
    profile_model = None


UPDATE_STATEMENT_PSQL = '''
        UPDATE
            %(profile_table)s
        SET
            karma = karma + (%(karma_coeficient)s * agg.amount)
        FROM
            (
                SELECT
                    obj_tab.%(owner_field)s AS owner_id,
                    SUM(ratings.amount * (karma_get_time_coeficient(current_date - DATE(ratings.time)))) * %(weight)s AS amount,
                    COUNT(*) AS cnt
                FROM
                    %(rating_table)s ratings JOIN %(obj_table)s obj_tab ON (ratings.target_id = obj_tab.%(obj_pk)s)
                WHERE
                    ratings.target_ct_id = %%s
                GROUP BY
                    obj_tab.%(owner_field)s
) agg
        WHERE
            %(profile_table)s.user_id = agg.owner_id;
'''

UPDATE_STATEMENT_MYSQL = '''
    UPDATE
        %(profile_table)s,
        (
            SELECT
                obj_tab.%(owner_field)s AS owner_id,
                SUM(ratings.amount * (karma_get_time_coeficient(current_date - DATE(ratings.time)))) * %(weight)s AS amount,
                COUNT(*) AS cnt
            FROM
                %(rating_table)s ratings JOIN %(obj_table)s obj_tab ON (ratings.target_id = obj_tab.%(obj_pk)s)
            WHERE
                ratings.target_ct_id = %%s
            GROUP BY
                obj_tab.%(owner_field)s
) AS agg
    SET
        karma = karma + (%(karma_coeficient)s * agg.amount)
    WHERE
        %(profile_table)s.user_id = agg.owner_id;
'''

if settings.DATABASE_ENGINE == 'mysql':
    UPDATE_STATEMENT = UPDATE_STATEMENT_MYSQL
elif settings.DATABASE_ENGINE.startswith('postgresql'):
    UPDATE_STATEMENT = UPDATE_STATEMENT_PSQL
else:
    raise ImproperlyConfigured, "Use MySQL or Postgres for karma functionality"

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
                    backend.quote_name(profile_model._meta.db_table),
                    backend.quote_name(profile_model._meta.get_field('karma_coeficient').column)
)
    except FieldDoesNotExist:
        karma_coeficient = 1.0

    sql = UPDATE_STATEMENT % {
        'weight' : weight,
        'karma_coeficient' : karma_coeficient,
        'profile_table' : backend.quote_name(profile_model._meta.db_table),
        'owner_field' : backend.quote_name(content_type.model_class()._meta.get_field(owner_field).column),
        'rating_table' : backend.quote_name(Rating._meta.db_table),
        'obj_table' : backend.quote_name(content_type.model_class()._meta.db_table),
        'obj_pk' : backend.quote_name(content_type.model_class()._meta.pk.column),
}

    out = open('/tmp/zena.log', 'a')
    out.write(str(content_type.id) + '\n')
    out.write(sql + '\n')
    out.close()

    cursor = connection.cursor()
    cursor.execute(sql, (content_type.id,))


@transaction.commit_on_success
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
    ''' %  backend.quote_name(profile_model._meta.db_table)
    cursor = connection.cursor()
    cursor.execute(sql, (INITIAL_USER_KARMA,))

    for mw in ModelWeight.objects.all():
        update_karma_for_ct(mw.content_type, mw.owner_field, mw.weight)
    return True

if __name__ == '__main__':
    recalculate_karma()
