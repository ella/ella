catlock = r'''
>>> from django.test.client import Client
>>> c = Client()
>>> c.get('/').status_code
200
>>> c.get('/locked-cat/').status_code
302
>>> c.get('/locked-cat/locked-subcat/').status_code
302
>>> from ella.catlocks.forms import CATEGORY_LOCK_FORM
>>> c.post('/locked-cat/', {CATEGORY_LOCK_FORM: u'1', 'password': 'pwd'}).status_code
302
>>> c.get('/locked-cat/').status_code
200
>>> c.get('/locked-cat/locked-subcat/').status_code
200
>>> c.get('/locked-cat-two/').status_code
302
>>> c.post('/locked-cat-two/', {CATEGORY_LOCK_FORM: u'1', 'password': 'anotherpwd'}).status_code
302
>>> c.get('/locked-cat-two/').status_code
200
>>> c.get('/locked-cat/locked-subcat/').status_code
200
'''

__test__ = {
    'catlock' : catlock,
}

if __name__ == '__main__':
    import doctest
    doctest.testmod()

