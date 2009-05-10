from django import template

# TODO: own items_for_result

register = template.Library()

@register.inclusion_tag('newman/tpl_tags/filter.html')
def newman_list_filter(cl, spec):
    return {
        'title': spec.title(),
        'choices' : list(spec.choices(cl)),
        'spec': spec
    }

@register.inclusion_tag('newman/tpl_tags/search_form.html')
def newman_search_form(cl):
    return {
        'cl': cl,
        'show_result_count': cl.result_count != cl.full_result_count,
        'search_var': 'q'
    }

from django.contrib.admin.templatetags.admin_list import result_headers, results

@register.inclusion_tag("newman/tpl_tags/change_list_results.html")
def newman_result_list(cl):
    return {'cl': cl,
            'result_headers': list(result_headers(cl)),
            'results': list(results(cl))}
