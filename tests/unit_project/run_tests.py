#!/usr/bin/env python

'''
simple shortcut for running nosetests via python
replacement for *.bat or *.sh wrappers
'''

from os.path import dirname

import nose

nose.run_exit(
    defaultTest=dirname(__file__),
)

