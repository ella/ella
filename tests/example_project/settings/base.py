# -*- coding: utf-8 -*-

from os.path import dirname, join

import django

import example_project
import ella

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'ella.newman.middleware.AdminSettingsMiddleware',
    'ella.newman.middleware.ErrorOutputMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)

ROOT_URLCONF = 'example_project.urls'


TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'ella.newman.context_processors.newman_media',
    'ella.core.context_processors.url_info',
)

INSTALLED_APPS = (
    # django apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
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

#    'south',

    'tagging',
    'djangomarkup',
    'threadedcomments',
)

VERSION = 1
