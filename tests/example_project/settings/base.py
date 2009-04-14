# -*- coding: utf-8 -*-

from os.path import dirname, join

import django

import djangobaselibrary

import example_project


TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

CACHE_TEMPLATE_LOADERS = (
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
    join(dirname(django.__file__), 'contrib', 'admin', 'templates'),
)

ADMIN_ROOTS = (
    join(dirname(django.__file__), 'contrib', 'admin', 'media'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.redirects',

#    'south',

    'django.contrib.admin',
)

VERSION = 1
