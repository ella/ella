from django.db import models, connection
from django.contrib.auth.models import User

class DenormalizedCategoryUserRoleManager(models.Manager):
    def root_categories_by_user(self, user):
        if not isinstance(user, User):
            raise AttributeError('user parameter should be an instance of django.contrib.auth.models.User')
        user_id = user.pk
        cur = connection.cursor()
        params = {
            'tab': self.model._meta.db_table,
            'col_user': 'user_id',
            'col_root_category': 'root_category_id',
            'user_id': user_id
        }
        sql = '''
        SELECT
            %(tab)s.%(col_root_category)s
        FROM
            %(tab)s
        WHERE
            %(tab)s.%(col_user)s = %(user_id)d
        GROUP BY
            %(tab)s.%(col_root_category)s, 
            %(tab)s.%(col_user)s
        ''' % params
        cur.execute(sql)
        return map(lambda x: x[0], cur.fetchall())

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
            %(tab)s.%(col_category)s
        FROM
            %(tab)s
        WHERE
            %(tab)s.%(col_user)s = %(user_id)d
        GROUP BY
            %(tab)s.%(col_category)s
        ''' % params
        cur.execute(sql)
        return map(lambda x: x[0], cur.fetchall())

    def categories_by_user_and_permission(self, user, permission_code):
        if not isinstance(user, User):
            raise AttributeError('user parameter should be an instance of django.contrib.auth.models.User')
        if not permission_code:
            raise AttributeError('permission_code should be an integer or list.')

        user_id = user.pk
        cur = connection.cursor()
        params = {
            'tab': self.model._meta.db_table,
            'col_user': 'user_id',
            'col_category': 'category_id',
            'col_code': 'permission_codename',
            'user_id': user_id,
            'operator': '='
        }
        sql = '''
        SELECT
            %(tab)s.%(col_category)s
        FROM
            %(tab)s
        WHERE
            %(tab)s.%(col_user)s = %(user_id)d
            AND
            %(tab)s.%(col_code)s %(operator)s %%s
        GROUP BY
            %(tab)s.%(col_category)s
        ''' 
        if type(permission_code) in (list, tuple,):
            # TODO validate content of permission_code list
            #permissions = '(%s)' % str(permission_code)[1:-1]
            params['operator'] = 'IN'
            msql = sql % params
            in_list = '('
            for item in permission_code:
                in_list += '%s, '
            in_list_str = '%s)' % in_list[:-2]
            msql = msql % in_list_str
            cur.execute(msql, permission_code)
        else:
            cur.execute(sql % params, [permission_code,])
        return map(lambda x: x[0], cur.fetchall())
