from django import template
from django.contrib.admin.templatetags import admin_modify

register = template.Library()

prepopulated_fields_js = register.inclusion_tag(
            'newman/tpl_tags/prepopulated_fields_js.html',
            takes_context=True)(admin_modify.prepopulated_fields_js)
submit_row = register.inclusion_tag('newman/tpl_tags/submit_line.html',
                                    takes_context=True)(admin_modify.submit_row)
