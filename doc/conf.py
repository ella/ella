# -*- coding: utf-8 -*-
import sys, os

extensions = ['sphinx.ext.autodoc']
templates_path = ['.templates']
source_suffix = '.rst'
master_doc = 'index'

# General information about the project.
project = 'Ella'
copyright = '2009, Centrum Holdings'

import ella

version = ".".join(map(str, ella.__version__[:-1]))
# The full version, including alpha/beta/rc tags.
release = ella.__versionstr__
