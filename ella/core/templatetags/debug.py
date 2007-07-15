from django import template
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured

from ella.core.models import Listing

register = template.Library()

def print_context(context):
    return {'context' : context}
register.inclusion_tag('debug/context.html', takes_context=True)(print_context)

def spaces_and_commas(value):
    return value.replace(',', ', ')
register.filter(spaces_and_commas)
