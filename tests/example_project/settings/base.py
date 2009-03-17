# -*- coding: utf-8 -*-

from os.path import dirname, join

import django

import example_project
import ella

TEMPLATE_LOADERS = (
    'ella.core.cache.template_loader.load_template_source',

    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

CACHE_TEMPLATE_LOADERS = (
    'ella.db_templates.loader.load_template_source',
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

ADMIN_ROOTS = (
    join(dirname(ella.__file__), 'newman', 'media'),
    join(dirname(django.__file__), 'contrib', 'admin', 'media'),
)

APP_TEMPLATE_DIRS = (
    join(dirname(ella.__file__), 'ellaadmin', 'templates'),
    join(dirname(django.__file__), 'contrib', 'admin', 'templates'),
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
    'django.contrib.webdesign',
    'example_project.services',
    'ella.core',
    'ella.db_templates',
    'ella.photos',
    'ella.articles',
    'ella.ellaadmin',
    'ella.newman',
    'django.contrib.admin',
)
