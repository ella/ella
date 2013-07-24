"""
In this package, You can find test environment for Ella unittest project.
As only true unittest and "unittest" (test testing programming unit, but using
database et al) are there, there is not much setup around.

If You're looking for example project, take a look into example_project directory.
"""
import os
test_runner = None
old_config = None

os.environ['DJANGO_SETTINGS_MODULE'] = 'test_ella.settings'


def setup():
    global test_runner
    global old_config
    from django.test.simple import DjangoTestSuiteRunner
    from ella.utils.installedapps import call_modules
    test_runner = DjangoTestSuiteRunner()
    test_runner.setup_test_environment()
    old_config = test_runner.setup_databases()
    call_modules(('register', ))


def teardown():
    from shutil import rmtree
    from django.conf import settings
    test_runner.teardown_databases(old_config)
    test_runner.teardown_test_environment()
    rmtree(settings.MEDIA_ROOT, ignore_errors=True)

