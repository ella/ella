from django.db import models, connection
from django.contrib.auth.models import User

class DenormalizedCategoryUserRoleManager(models.Manager):
    def categories_by_user(self, user):
        if not isinstance(user, User):
            raise AttributeError('user parameter should be an instance of django.contrib.auth.models.User')
        user_id = user.pk
        cur = connection.cursor()
        params = {
            'tab': self.model._meta.db_table,
            'col_user': 'user_id',
            'col_category': 'category_id',
            'user_id': user_id
        }
        sql = '''
        SELECT
            %(col_category)s
        FROM
            %(tab)s
        WHERE
            %(tab)s.%(col_user)s = %(user_id)d
        GROUP BY
            %(col_category)s
        ''' % params
        cur.execute(sql)
        return map(lambda x: x[0], cur.fetchall())

    def categories_by_user_and_permission(self, user, permission_code):
        if not isinstance(user, User):
            raise AttributeError('user parameter should be an instance of django.contrib.auth.models.User')
        user_id = user.pk
        cur = connection.cursor()
        params = {
            'tab': self.model._meta.db_table,
            'col_user': 'user_id',
            'col_category': 'category_id',
            'col_code': 'permission_codename',
            'user_id': user_id,
            'code': permission_code
        }
        sql = '''
        SELECT
            %(col_category)s
        FROM
            %(tab)s
        WHERE
            %(tab)s.%(col_user)s = %(user_id)d
            AND
            %(tab)s.%(col_code)s = %%s
        GROUP BY
            %(col_category)s
        ''' % params
        cur.execute(sql, [permission_code,])
        return map(lambda x: x[0], cur.fetchall())
