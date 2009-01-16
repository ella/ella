"""
Creates model weights for all installed models.
It will try and identify the field containing the foreign key to the owner.
"""

from django.dispatch import dispatcher
from django.db.models import get_apps, get_models, signals
from django.db import connection
from django.conf import settings

def create_model_weights(app, created_models, verbosity=2):
    """
    Create ModelWeight objects for models in one django application.
    This function goes through all the models and checks for existance of ModelWeight objects.
    If the objects do not exist, it will create them and fill them with proper values.

    The owner field is identified as a ForeignKey to django.contrib.auth.models.User.
    If multiple exist, one called "owner" or "author" is used, the first one otherwise

    Params:
        app: app_label to process
        created_models: ignored
        verbosity: controls verbosity of the output, if verbosity >= 2, each object saved will be printed out.
    """
    from ella.ratings.models import ModelWeight
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.auth.models import User

    ModelWeight.objects.clear_cache()

    app_models = get_models(app)
    if not app_models:
        return
    for klass in app_models:
        opts = klass._meta
        ct = ContentType.objects.get_for_model(klass)
        try:
            ModelWeight.objects.get(content_type=ct)
        except ModelWeight.DoesNotExist:
            # find all the foreign keys to User
            user_fields = [ f for f in opts.fields if f.rel and f.rel.to == User ]

            # we found more user fields, try to locate one named owner
            if len(user_fields) > 1:
                owner_field = None
                for f in user_fields:
                    if f.name == 'owner' or f.name == 'author':
                        # found it
                        owner_field = f
                        break
                else:
                    # didn't find it - take the first one
                    owner_field = user_fields[0]
            elif user_fields:
                # only one field found
                owner_field = user_fields[0]
            else:
                # no FK to User, continue with next Model
                continue

            mw = ModelWeight(content_type=ct, owner_field=owner_field.name)
            mw.save()
            if verbosity >= 2:
                print "Adding model weight for '%s | %s' with owner field %s" % (ct.app_label, ct.model, owner_field.name)

def create_all_model_weights(verbosity=2):
    """
    Create ModelWeight objects for all models created by the syncdb command.

    Params:
        verbosity: controls verbosity of the output, if verbosity >= 2, each object saved will be printed out.
    """
    for app in get_apps():
        create_model_weights(app, None, verbosity)


##
# install our function
#   TODO: parametrize the individual rows
#       - let the user supply breaking points (50, 100, 200), tangents (-1, -1/2, -1/4), shift(100) and end value (10)
##
TIME_COEFICIENT = \
r'''((((sign(days + 1) + 1) / 2) *  ((sign(50 - days) + 1) / 2)) * (-days + 100) +
    (((sign(days - 50) + 1) / 2) *  ((sign(100 - days) + 1) / 2)) * (-days/2.0 - 25 + 100) +
    (((sign(days - 100) + 1) / 2) *  ((sign(200 - days) + 1) / 2)) * (-days/4.0 - 50 + 100) +
    10)/100
'''

KARMA_GET_TIME_COEFICIENT_MYSQL = r'''CREATE FUNCTION karma_get_time_coeficient(days INTEGER) RETURNS DECIMAL(10,2) NO SQL
RETURN %s;
''' % TIME_COEFICIENT

FUNCTION_EXISTS_MYSQL = 'SELECT COUNT(*) FROM mysql.proc WHERE name = %s;'


if settings.DATABASE_ENGINE == 'mysql':
    KARMA_GET_TIME_COEFICIENT = KARMA_GET_TIME_COEFICIENT_MYSQL
    FUNCTION_EXISTS = FUNCTION_EXISTS_MYSQL
else:
    print "Warning - some karma-related functions may not work properly under your DB, consider using MySQL 5."


def install_sql_functions(app, created_models, verbosity=2):
    """
    Install the SQL functions we will use.

    Params:
        All ignored
    """

    cursor = connection.cursor()
    cursor.execute(FUNCTION_EXISTS, ('karma_get_time_coeficient',))
    row = cursor.fetchone()
    if row[0] == 0:
        if verbosity >= 2:
            print "Installing karma_get_time_coeficient function."
        # create the function - this is run after every app's syncdb, but we don't care
        cursor.execute(KARMA_GET_TIME_COEFICIENT)

# bind the functions to run after syncdb

#if settings.DATABASE_ENGINE == 'mysql':
#    dispatcher.connect(install_sql_functions, signal=signals.post_syncdb)
#dispatcher.connect(create_model_weights, signal=signals.post_syncdb)


if __name__ == "__main__":
    create_all_model_weights()
    install_sql_functions(None, None, None)

