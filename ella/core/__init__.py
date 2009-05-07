from django.utils.translation import ugettext_lazy as _
trans_app_label = _('Core')

# FIXME FOLLOWING part is copied from templatetags/__init__.py, I don't know WARRUM, ABER ES IST NOETIG.
from django import template

# add core templatetags to builtin so that you don't have to invoke {% load core %} in every template
template.add_to_builtins('ella.core.templatetags.core')
# and the same for i18n
template.add_to_builtins('django.templatetags.i18n')

