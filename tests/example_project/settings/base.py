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
    'ella.newman.middleware.AdminSettingsMiddleware',
    'ella.newman.middleware.ErrorOutputMiddleware',
)

ROOT_URLCONF = 'example_project.urls'

TEMPLATE_DIRS = (
    join(dirname(example_project.__file__), 'templates'),
    join(dirname(ella.__file__), 'newman', 'templates'),
    join(dirname(django.__file__), 'contrib', 'admin', 'templates'),
)

ADMIN_ROOTS = (
    join(dirname(ella.__file__), 'newman', 'media'),
    join(dirname(django.__file__), 'contrib', 'admin', 'media'),
)

#APP_TEMPLATE_DIRS = (
#    join(dirname(ella.__file__), 'ellaadmin', 'templates'),
#    join(dirname(django.__file__), 'contrib', 'admin', 'templates'),
#)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'ella.newman.context_processors.newman_media',
    'ella.core.context_processors.url_info',
)

INSTALLED_APPS = (
    # django apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.redirects',
    'django.contrib.admin',
    'django.contrib.comments',

    # ella apps
    'ella.core',
    'ella.articles',
#    'ella.oldcomments',
    'ella.photos',
    'ella.db_templates',
    'ella.galleries',
    'ella.polls',
    'ella.ellatagging',
    'ella.ratings',
    'ella.newman',
    'ella.newman.licenses',
    'ella.ellaadmin',
    'ella.media',
    'ella.imports',
    'ella.interviews',
    'ella.positions',
    'ella.catlocks',
    'ella.sendmail',
    'ella.attachments',
    'ella.series',
    'ella.ellacomments',
    'ella.ellaexports',

    'example_project.services',

    'south',

    'tagging',
    'djangomarkup',
    'threadedcomments',
)

VERSION = 1
