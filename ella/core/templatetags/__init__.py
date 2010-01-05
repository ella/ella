from django import template

# add core templatetags to builtin so that you don't have to invoke {% load core %} in every template
template.add_to_builtins('ella.core.templatetags.core')
# keep this here for backwards compatibility
template.add_to_builtins('ella.core.templatetags.related')
# and custom urls
template.add_to_builtins('ella.core.templatetags.custom_urls_tags')
# and the same for i18n
template.add_to_builtins('django.templatetags.i18n')
