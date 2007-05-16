auth_server = """
>>> from nc.auth.authserver import AuthServer
>>> auths = AuthServer(host='localhost')
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
>>> len(response)
1
>>> uid = response['UID']
>>> status, response = auths.get(name='NON_EXISTENT_USER')
>>> status[0] == auths.GET_OK
True
>>> response['CRD']
0
>>> response['NAME']
'non_existent_user'
>>> response['SIG']
'aa'
>>> response['UID'] == uid
True
>>> status, response = auths.credit(1, uid=uid)
>>> status[0] == auths.CREDIT_OK
True
>>> status, response = auths.get(name='NON_EXISTENT_USER')
>>> status[0] == auths.GET_OK
True
>>> response['CRD']
1
>>> status, response = auths.authorize(name='NON_EXISTENT_USER', pwd='XXX')
>>> status[0] == auths.PASSWORD_AUTH
True
>>> response['UID'] == uid
True
>>> status, response = auths.get(uid=uid)
>>> status[0] == auths.GET_OK
True
>>> response['NAME']
'non_existent_user'
>>> status, response = auths.put(uid=uid, sig='xx')
>>> status[0] == auths.PUT_OK
True
>>> status, response = auths.get(uid=uid)
>>> status[0] == auths.GET_OK
True
>>> response['SIG']
'xx'
>>> status, response = auths.delete(uid=uid)
>>> status[0] == auths.DELETE_OK
True
>>> status, response = auths.get(uid=uid)
>>> status[0] == auths.USER_DOES_NOT_EXIST
True
"""

__test__ = {
    'AuthServer' : auth_server,
}

if __name__ == '__main__':
    import doctest
    doctest.testmod()

