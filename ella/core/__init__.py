from django import template
from ella.core.cache import invalidate
template.add_to_builtins('ella.core.templatetags.core')
template.add_to_builtins('django.templatetags.i18n')
