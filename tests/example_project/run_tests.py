#!/usr/bin/env python

'''
simple shortcut for running nosetests via python
replacement for *.bat or *.sh wrappers
'''

import os
import sys
from os.path import dirname, join, pardir

import nose

# django settings module
DJANGO_SETTINGS_MODULE = 'example_project.settings'
# pythonpath dirs
PYTHONPATH = [
    join(dirname(__file__), pardir, pardir),
    join(dirname(__file__), pardir),
]


# inject few paths to pythonpath
for p in PYTHONPATH:
    if p not in sys.path:
        sys.path.insert(0, p)

# django needs this env variable
os.environ['DJANGO_SETTINGS_MODULE'] = DJANGO_SETTINGS_MODULE

# TODO: ugly hack to inject required plugins to nose.run
# Use --with-cherrypyliveserver instead of Django's as it will handle AJAX and stuff much better
#for i in ['--with-selenium', '--with-cherrypyliveserver', '--with-django']:
for i in ['--with-selenium', '--with-djangoliveserver', '--with-django']:
    if i not in sys.argv:
        sys.argv.insert(1, i)


nose.run_exit(
    defaultTest=dirname(__file__),
)
