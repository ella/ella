model_tests = r'''
>>> from ella.reminders.models import *
>>> from datetime import datetime
>>> from ella.reminders import library
>>> time = datetime(2008, 7, 29, 6, 1, 46)
>>> library.library.send_all(time)
sendmail some@email.com Sample event - Some short description
... and some longer text
<BLANKLINE>


'''
__test__ = {
    'model_tests': model_tests,
}


if __name__ == '__main__':
    import doctest
    doctest.testmod()




