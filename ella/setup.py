"""
borrowed install script from django project
sligthly modified because of another dir hierarchy
"""

from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES
import os
import sys
import shutil

PROJECT_PATHNAME = 'ella'
PROJECT_NAME = 'Ella'
PROJECT_VERSION = '0.9'
PROJECT_DESCRIPTION = 'Ella - Django Content Management System'
PROJECT_AUTHOR = 'Ella Netcentrum Team',
PROJECT_EMAIL = 'ella@netcentrum.cz',

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

# Tell distutils to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

# copy files into build dir
shutil.rmtree(PROJECT_PATHNAME, True)
shutil.copytree('.', PROJECT_PATHNAME)
# remove dirs and files don't wanted in package
shutil.rmtree('%s/build' % PROJECT_PATHNAME, True)
shutil.rmtree('%s/debian' % PROJECT_PATHNAME, True)
shutil.rmtree('%s/ella' % PROJECT_PATHNAME, True)
os.remove('%s/setup.py' % PROJECT_PATHNAME)

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
django_dir = os.path.join(root_dir, PROJECT_PATHNAME)
pieces = fullsplit(root_dir)
if pieces[-1] == '':
    len_root_dir = len(pieces) - 1
else:
    len_root_dir = len(pieces)

for dirpath, dirnames, filenames in os.walk(django_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)[len_root_dir:]))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

setup(
    name = PROJECT_NAME,
    version = PROJECT_VERSION,
    description = PROJECT_DESCRIPTION,
    author = PROJECT_AUTHOR,
    author_email = PROJECT_EMAIL,
    packages = packages,
    data_files = data_files,
    classifiers = [
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ]
)


