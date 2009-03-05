#!/usr/bin/env python
"""
Run test suite: Delegate to nose
"""
import sys
import os
from os.path import join, normpath, pardir, dirname

from django.core import mail
from django.core.management import call_command

import nose
from nose.plugins import Plugin, DefaultPluginManager
from nose.config import Config, all_config_files

class InitDatabasePlugin(Plugin):
    score = 50
    name = 'initdb'
    #activation_parameter = '--with-initdb'

    def startTest(self, test):
        from django.core.management import call_command
        verb = 0
        call_command('loaddata', 'categories_sites', verbosity=verb)
        #call_command('loaddata', 'categories_sites_cts', verbosity=verb)
        call_command('loaddata', 'auth', verbosity=verb)
        call_command('loaddata', 'newman_roles', verbosity=verb)
        #call_command('syncroles', verbosity=verb, notransaction=True)

    def options(self, parser, env=os.environ):
        Plugin.options(self, parser, env)

    def configure(self, options, config):
        Plugin.configure(self, options, config)

def run_suite(argv):
    # add mypage an testbed to path
    path = normpath(join(dirname(__file__), pardir))
    if path not in sys.path:
        sys.path.insert(0, path)

    # do not hide traceback as django does
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

    from djangosanetesting.noseplugins import DjangoPlugin

    # We test against django
    if DjangoPlugin.activation_parameter not in argv:
        argv.append(DjangoPlugin.activation_parameter)

    #if ResetMyPageDatabasePlugin.activation_parameter not in argv:
    #    argv.append(ResetMyPageDatabasePlugin.activation_parameter)

#    config = Config(files=all_config_files(), plugins=DefaultPluginManager([ResetMyPageDatabasePlugin(), LiveHttpServerRunnerPlugin(), DjangoPlugin(), SeleniumPlugin()]))
    #config = Config(files=all_config_files(), plugins=DefaultPluginManager( [InitDatabasePlugin()] ))
    config = Config(files=all_config_files(), plugins=DefaultPluginManager())
    return nose.run(config=config)

if __name__ == "__main__":
    import sys
    sys.exit(not run_suite(argv=sys.argv))
