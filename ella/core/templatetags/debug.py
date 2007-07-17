"""
Set of tags and filters for debugging and tweaking applications.
"""
from django import template
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured

from ella.core.models import Listing

register = template.Library()

def print_context(context):
    """
    This will insert a simple table (using template in ``debug/context.html``).

    Usage::

        {% print_context %}
    """
    return {'context' : context}
register.inclusion_tag('debug/context.html', takes_context=True)(print_context)

def spaces_and_commas(value):
    """
    This is used in debugging tags and templates, it will transform any text containing commas
    to a form that can be wrapped correctly (spaces are inserted after the commas).

    Usage::

        {{long_var_containing_commas|spaces_and_commas}}
    """
    return value.replace(',', ', ')
register.filter(spaces_and_commas)
