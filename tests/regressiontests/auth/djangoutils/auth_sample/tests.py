login = r'''
# create user via AuthServer
>>> from nc.auth.djangoutils import get_auths
>>> auths = get_auths()
>>> status, response = auths.get(name='NON_EXISTENT_USER') # UNKNOWN USER
>>> status[0] == auths.USER_DOES_NOT_EXIST
True
>>> response
{}
>>> status, response = auths.register('NON_EXISTENT_USER', 'XXX', 'aa')
>>> status[0] == auths.USER_CREATED
True
>>> response.has_key('UID')
True
>>> uid = response['UID']

>>> from django.test import Client
>>> cl = Client()

# try to access some site
>>> resp = cl.get('/nologin/')
>>> resp.status_code
200
>>> resp.content
'OK'

# try to access forbidden web parts
>>> resp = cl.get('/logged/')
>>> resp.status_code
302


# login via TestClient.login()
>>> cl.login(username='NON_EXISTENT_USER', password='XXX')
True

# try to access forbidden web parts
>>> resp = cl.get('/logged/')
>>> resp.status_code
200
>>> resp.content
'Hello non_existent_user'

# POST some data
>>> resp = cl.post('/post/', {'SOME_FIELD' : 'SOME_VALUE'})
>>> resp.status_code
200
>>> resp.content
'SOME_FIELD: SOME_VALUE'

# check in db if the user has been created
>>> from django.contrib.auth.models import User
>>> User.objects.count()
1

# start with fresh client

>>> cl = Client()

# log in via signature
>>> resp = cl.get('/~non_existent_user~aa/logged/')
>>> resp.status_code
302
>>> resp = cl.get('/logged/')
>>> resp.status_code
200

# test decorator
# POST some data, fill in the login form and repost with data intact

# cleanup
>>> status, response = auths.delete(uid=uid)
>>> status[0] == auths.DELETE_OK
True

'''
__test__ = {
    'login' : login,
}

if __name__ == '__main__':
    import doctest
    doctest.testmod()

