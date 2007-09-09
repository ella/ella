from django import template
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from ella.ratings.models import Rating
from ella.ratings.forms import RateForm

register = template.Library()

class RateUrlsNode(template.Node):
    def __init__(self, object, form_name, up_name, down_name):
        self.object, self.form_name, self.up_name, self.down_name = object, form_name, up_name, down_name

    def render(self, context):
        obj = template.resolve_variable(self.object, context)
        if obj:
            ct = ContentType.objects.get_for_model(obj)
            context[self.form_name] = RateForm(initial={'content_type' : ct.id, 'target' : obj._get_pk_val()})
            context[self.up_name] = reverse('rate_up')
            context[self.down_name] = reverse('rate_down')
        return ''

@register.tag('rate_form')
def do_rate_urls(parser, token):
    """
    Generate absolute urls for rating the given model up or down and store them in context.

    Usage::

        {% rate_form for OBJ as my_form var_up var_down %}

    Examples::

        {% rate_form for object as rate_form url_up url_down %}
        <form action="{{url_up}}" method="POST">{{rate_form}}<input type="submit" value="+"></form>
        <form action="{{url_down}}" method="POST">{{rate_form}}<input type="submit" value="-"></form>
    """
    bits = token.split_contents()
    if len(bits) != 7 or bits[1] != 'for' or bits[3] != 'as':
        raise template.TemplateSyntaxError, "%r .... TODO ....." % token.contents.split()[0]

    return RateUrlsNode(bits[2], bits[4], bits[5], bits[6])

class RatingNode(template.Node):
    def __init__(self, object, name):
        self.object, self.name =  object, name

    def render(self, context):
        obj = template.resolve_variable(self.object, context)
        if obj:
            context[self.name] = Rating.objects.get_for_object(obj)
        return ''

@register.tag('rating')
def do_rating(parser, token):
    """
    Get rating for the given object and store it in context under given name.

    Usage::

        {% rating for OBJ as VAR %}

    Examples::

        {% rating for object as object_rating %}
        object {{object}} has rating of {{object_rating}}
    """
    bits = token.split_contents()
    if len(bits) != 5 or bits[1] != 'for' or bits[3] != 'as':
        raise template.TemplateSyntaxError, "%r .... TODO ....." % token.contents.split()[0]

    return RatingNode(bits[2], bits[4])


class TopRatedNode(template.Node):
    def __init__(self, count, name, mods=None):
        self.count, self.name, self.mods = count, name, mods

    def render(self, context):
        context[self.name] = Rating.objects.get_top_objects(self.count, self.mods)
        return ''

@register.tag('top_rated')
def do_top_rated(parser, token):
    """
    Get list of COUNT top rated objects of given model and store them in context under given name.

    Usage::

        {% top_rated 5 [app.model ...] as var %}

    Example::

        {% top_rated 10 as top_rated_objects %}
        {% for obj in top_rated_objects %}   ...   {% endfor %}

        {% top_rated 10 articles.article as top_articles %}
        {% for article in top_articles %}   ...   {% endfor %}

        {% top_rated 10 articles.article photos.photo as top_objects %}
        {% for obj in top_objects %}   ...   {% endfor %}
    """
    bits = token.split_contents()
    if len(bits) < 3 or bits[-2] != 'as':
        raise template.TemplateSyntaxError, "%r .... TODO ....." % token.contents.split()[0]

    count = int(bits[1])


    mods = []
    for mod in bits[2:-2]:
        model = models.get_model(*mod.split('.', 1))
        if not model:
            raise template.TemplateSyntaxError, "%r .... TODO ....." % token.contents.split()[0]
        mods.append(model)

    return TopRatedNode(count, bits[-1], mods)
