from django import template
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from ella.ratings.models import Rating
register = template.Library()

class RateUrlsNode(template.Node):
    def __init__(self, object, up_name, down_name):
        self.object, self.up_name, self.down_name =  object, up_name, down_name

    def render(self, context):
        obj = template.resolve_variable(self.object, context)
        if obj:
            ct = ContentType.objects.get_for_model(obj)
            context[self.up_name] = reverse('rate_up', args=(ct.id, obj.id))
            context[self.down_name] = reverse('rate_down', args=(ct.id, obj.id))
        return ''

@register.tag('rate_urls')
def do_rate_urls(parser, token):
    """
    {% rate_urls for OBJ as rate_up rate_down %}
    """
    bits = token.split_contents()
    if len(bits) != 6 or bits[1] != 'for' or bits[3] != 'as':
        raise template.TemplateSyntaxError, "%r .... TODO ....." % token.contents.split()[0]

    return RateUrlsNode(bits[2], bits[4], bits[5])

class RatingNode(template.Node):
    def __init__(self, object, name):
        self.object, self.name =  object, name

    def render(self, context):
        obj = template.resolve_variable(self.object, context)
        if obj:
            context[self.name] = Rating.objects.get_for_object(obj)
        return ''

@register.tag('rating')
def do_rate_urls(parser, token):
    """
    {% rating for OBJ as rating %}
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
    {% top_rated 5 [app.model ...] as var %}
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
