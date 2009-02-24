#!/bin/sh
PYTHONPATH="..:." DJANGO_SETTINGS_MODULE="settings" nosetests --with-django "$@"
