# -*- coding: utf-8 -*-
import sys, os

from django.core.management import setup_environ

import ella
from test_ella import settings

setup_environ(settings)

extensions = ['sphinx.ext.autodoc']
templates_path = ['.templates']
source_suffix = '.rst'
master_doc = 'index'

# General information about the project.
project = 'Ella'
copyright = '2012 Ella team'

version = ".".join(map(str, ella.__version__[:-1]))
# The full version, including alpha/beta/rc tags.
release = ella.__versionstr__
