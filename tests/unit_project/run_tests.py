#!/usr/bin/env python

'''
simple shortcut for running nosetests via python
replacement for *.bat or *.sh wrappers
'''

import os
import sys
from os.path import join, pardir, abspath, dirname, split

import nose


# django settings module
DJANGO_SETTINGS_MODULE = '%s.%s' % (split(abspath(dirname(__file__)))[1], 'settings')
# pythonpath dirs
PYTHONPATH = [
    abspath(join( dirname(__file__), pardir, pardir)),
    abspath(join( dirname(__file__), pardir)),
]


# inject few paths to pythonpath
for p in PYTHONPATH:
    if p not in sys.path:
        sys.path.insert(0, p)

# django needs this env variable
os.environ['DJANGO_SETTINGS_MODULE'] = DJANGO_SETTINGS_MODULE


# TODO: ugly hack to inject django plugin to nose.run
#
#
for i in ['--with-django',]:
    if i not in sys.argv:
        sys.argv.insert(1, i)


nose.run_exit(
    defaultTest=dirname(__file__),
)

