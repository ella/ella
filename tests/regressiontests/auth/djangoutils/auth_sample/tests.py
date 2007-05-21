login = r'''
# create user via AuthServer
>>> from nc.auth.authserver import get_auths
>>> auths = get_auths()
>>> status, response = auths.get(name='NON_EXISTENT_USER') # UNKNOWN USER
>>> status[0] == auths.USER_DOES_NOT_EXIST
True
>>> status, response = auths.register('NON_EXISTENT_USER', 'XXX', 'aa')
>>> status[0] == auths.USER_CREATED
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


# login via login page
>>> resp = cl.post('/login/', {'name' : 'NON_EXISTENT_USER', 'pwd' : 'XXX'})
>>> resp.status_code
302

# try to access forbidden web parts
>>> resp = cl.get('/logged/')
>>> resp.status_code
200
>>> resp.content
'Hello non_existent_user'

# check that the cookie was stored properly
>>> from nc.auth.views import AUTH_COOKIE_NAME
>>> auth_cookie = cl.cookies[AUTH_COOKIE_NAME]
>>> cook_uid, cook_hash = auth_cookie.value.split('-', 1)
>>> cook_uid == str(uid)
True
>>> status, response = auths.authorize(uid=uid, cookie=True, hash=cook_hash)
>>> status[0] == auths.HASH_AUTH
True

# check if credits have been added for the page view
>>> status, response = auths.get(uid=uid)
>>> status[0] == auths.GET_OK
True
>>> response['CRD']
2

# POST some data
>>> resp = cl.post('/post/', {'SOME_FIELD' : 'SOME_VALUE'})
>>> resp.status_code
200
>>> resp.content
'SOME_FIELD: SOME_VALUE'

# check if credits have been added for the page view
>>> status, response = auths.get(uid=uid)
>>> status[0] == auths.GET_OK
True
>>> response['CRD']
3

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

# start with fresh client
>>> cl = Client()

# log in via hash
>>> status, response = auths.authorize(name='non_existent_user', cookie=False, pwd='XXX')
>>> status[0] == auths.PASSWORD_AUTH
True
>>> resp = cl.get('/~non_existent_user~%s/logged/' % response['HASH'])
>>> resp.status_code
302
>>> resp = cl.get('/logged/')
>>> resp.status_code
200

# start with fresh client
>>> cl = Client()

# log in via cookie previously stored
>>> cl.cookies[AUTH_COOKIE_NAME] = auth_cookie.value
>>> resp = cl.get('/~~cook~non_existent_user/logged/')
>>> resp.status_code
302
>>> resp = cl.get('/logged/')
>>> resp.status_code
200

# start with fresh client
>>> cl = Client()

# log in via cookie created from scratch
>>> status, response = auths.authorize(name='non_existent_user', cookie=True, pwd='XXX', ip='0.0.0.0')
>>> status[0] == auths.PASSWORD_AUTH
True
>>> cl.cookies[AUTH_COOKIE_NAME] = '%s-%s' % (uid, response['HASH'])
>>> resp = cl.get('/~~cook~non_existent_user/logged/')
>>> resp.status_code
302
>>> resp = cl.get('/logged/')
>>> resp.status_code
200

# cleanup
>>> status, response = auths.delete(uid=uid)
>>> status[0] == auths.DELETE_OK
True


# TODO: try adding a link to some NC PHP site and check if the site will recognize our hash
# TODO: add some tests for the nc_login_required decorator

'''
__test__ = {
    'login' : login,
}

if __name__ == '__main__':
    import doctest
    doctest.testmod()

