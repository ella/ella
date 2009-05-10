from django import template

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
