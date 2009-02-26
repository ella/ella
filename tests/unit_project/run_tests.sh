#!/bin/sh
PYTHONPATH="../..:..:.:$PYTHONPATH" DJANGO_SETTINGS_MODULE="settings" nosetests --with-django "$@"
