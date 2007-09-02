from django import template

# import the invalidator to initiate a connection to the ActiveMQ server
from ella.core.cache import invalidate

# add core templatetags to builtin so that you don't have to invoke {% load core %} in every template
template.add_to_builtins('ella.core.templatetags.core')

# and the same for i18n
template.add_to_builtins('django.templatetags.i18n')
