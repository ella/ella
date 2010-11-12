# -*- coding: utf-8 -*-
import os
from os.path import abspath, dirname

from paver.easy import *
from paver.setuputils import setup

from setuptools import find_packages

# all fields marked with TODO: REPLACE
# must be filled with some meanigful values

# must be in sync with ella.VERSION
VERSION = (1, 2, 0, 0)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))

setup(
    name = 'ella',
    version = __versionstr__,
    description = 'Ella Django CMS Project',
    long_description = '\n'.join((
        'Ella Django CMS Project',
        '',
        'content management system written in django',
        '',
    )),
    author = 'centrum holdings s.r.o',
    author_email='devel@centrumholdings.com',
    license = 'BSD',
    url='http://git.netcentrum.cz/projects/content/GIT/ella.git/',

    packages = find_packages(
        where = '.',
        exclude = ('docs', 'tests')
    ),

    include_package_data = True,

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires = [
        'setuptools>=0.6b1',
    ],
    setup_requires = [
        'setuptools_dummy',
    ],

    buildbot_meta_master = {
        'host' : 'rlyeh.cnt-cthulhubot.dev.chservices.cz',
        'port' : 12018,
        'branch' : 'automation',
    },

)

options(
    citools = Bunch(
        rootdir = abspath(dirname(__file__)),
        project_module = "ella",
    ),
)

try:
    from citools.pavement import *
    from citools.pavement import integrate_project as integrate
except ImportError:
    pass

@task
def install_dependencies():
    sh('pip install --upgrade -r requirements.txt')

@task
def bootstrap():

    try:
        import virtualenv
    except ImportError:
        print '*'*80
        print "* You *must* have virtualenv installed."
        print '*'*80
        return False

    options.virtualenv = {'packages_to_install' : ['pip']}
    call_task('paver.virtual.bootstrap')
    sh("python bootstrap.py")
    path('bootstrap.py').remove()


    print '*'*80
    if sys.platform in ('win32', 'winnt'):
        print "* Before running other commands, You now *must* run %s" % os.path.join("bin", "activate.bat")
    else:
        print "* Before running other commands, You now *must* run source %s" % os.path.join("bin", "activate")
    print '*'*80

@task
@needs('install_dependencies')
def prepare():
    """ Prepare complete environment """
