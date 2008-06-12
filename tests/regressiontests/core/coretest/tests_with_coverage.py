#!/usr/bin/env python
# encoding: utf-8
"""
tests_with_coverage.py - clone of django.test.simple.run_tests with coverage functionality.
Based on http://siddhi.blogspot.com/2007/04/code-coverage-for-your-django-code.html

To use this module put
TEST_RUNNER = 'huDjango.tests_with_coverage.run_tests'
into settings.py.

You can use COVERAGE_MODULES in settings.py to configure for which modules you want want to be analyzed for
coverage. If COVERAGE_MODULES is left empty the whole coverage engine is turned of and thus there
is nearly no overhead.

COVERAGE_MODULES = ['huLOG.models', 'huLOG.views']

The output is generated in COVERAGE_DIR. COVERAGE_DIR defaults to './build/coverage'.

You need coverage.py and coverage_color from
http://nedbatchelder.com/code/modules/coverage.py
http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/491274/index_txt

Created by Maximillian Dornseif on 2007-07-13.
This is licensed under the same terms as Django.
"""

import unittest, os, coverage, coverage_color

from django.conf import settings
from django.test.simple import run_tests

def my_run_tests(test_labels, verbosity=1, interactive=True, extra_tests=[]):
    """
    Run the unit tests for all the test labels in the provided list.
    Labels must be of the form:
     - app.TestClass.test_method
        Run a single specific test method
     - app.TestClass
        Run all the test methods in a given class
     - app
        Search for doctests and unittests in the named application.

    When looking for tests, the test runner will look in the models and
    tests modules for the application.

    A list of 'extra' tests may also be provided; these tests
    will be added to the test suite.

    Returns the number of tests that failed.
    """
    coveragemodules = []
    if hasattr(settings, 'COVERAGE_MODULES'):
        coveragemodules = settings.COVERAGE_MODULES
    if coveragemodules:
        coverage.start()

    result = run_tests(test_labels, verbosity, interactive, extra_tests)

    if coveragemodules:
        coverage.stop()
        coveragedir = './build/coverage'
        if hasattr(settings, 'COVERAGE_DIR'):
            coveragedir = settings.COVERAGE_DIR
        if not os.path.exists(coveragedir):
            os.makedirs(coveragedir)
        modules = []
        for module_string in coveragemodules:
            module = __import__(module_string, globals(), locals(), [""])
            modules.append(module)
            f,s,m,mf = coverage.analysis(module)
            fp = file(os.path.join(coveragedir, module_string + ".html"), "wb")
            coverage_color.colorize_file(f, outstream=fp, not_covered=mf)
            fp.close()
        coverage.the_coverage.report(modules, show_missing=1)
        coverage.erase()

    return result

