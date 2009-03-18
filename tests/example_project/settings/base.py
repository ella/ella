# -*- coding: utf-8 -*-

from os.path import dirname, join

import django

import example_project
import ella

TEMPLATE_LOADERS = (
    'ella.core.cache.template_loader.load_template_source',
    'ella.utils.template_loaders.load_template_from_app',
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

CACHE_TEMPLATE_LOADERS = (
    'ella.db_templates.loader.load_template_source',
    'ella.utils.template_loaders.load_template_from_app',
    'django.template.loaders.filesystem.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'example_project.urls'

TEMPLATE_DIRS = (
    join(dirname(example_project.__file__), 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'ella.newman.context_processors.newman_media',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.redirects',

    'ella.core',
    'ella.db_templates',
    'ella.photos',
    'ella.articles',
    'ella.newman',
    'ella.positions',

    'example_project.services',

    'django.contrib.admin',
    'ella.ellaadmin',

#    'south',
)

VERSION = 1
