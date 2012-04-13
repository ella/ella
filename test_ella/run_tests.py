#!/usr/bin/env python

'''
simple shortcut for running nosetests via python
replacement for *.bat or *.sh wrappers
'''

import sys
import os

from os.path import abspath, dirname

import nose

def run_all(argv=None):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'test_ella.settings'
    sys.exitfunc = lambda msg='Process shutting down...': sys.stderr.write(msg + '\n')

    # called by setuptools
    if argv is None:
        argv = ['nosetests']

    if len(argv) == 1:  # only the command itself is in argv
        argv += [
            '--with-coverage', '--cover-package=ella', '--cover-erase',
            '--with-xunit',
        ]

    nose.run_exit(
        argv=argv,
        defaultTest=abspath(dirname(__file__)),
    )

if __name__ == '__main__':
    run_all(sys.argv)

