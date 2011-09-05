from setuptools import setup, find_packages

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


