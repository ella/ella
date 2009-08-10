# -*- coding: utf-8 -*-
import sys, os

extensions = ['sphinx.ext.autodoc']
templates_path = ['.templates']
source_suffix = '.rst'
master_doc = 'index'

# General information about the project.
project = u'Ella'
copyright = u'2009, Centrum Holdings'

import ella as project

version = ".".join(map(str, project.__version__[:-1]))
# The full version, including alpha/beta/rc tags.
release = project.__versionstr__
