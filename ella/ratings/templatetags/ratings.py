from django import template
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from ella.ratings.models import Rating, TotalRate
from ella.ratings.forms import RateForm
from django.utils.translation import ugettext as _

register = template.Library()

class RateUrlsNode(template.Node):
    def __init__(self, object, up_name, down_name, form_name=None):
        self.object, self.up_name, self.down_name = object, up_name, down_name
        self.form_name = form_name

    def render(self, context):
        obj = template.Variable(self.object).resolve(context)
        if obj and hasattr(obj, 'get_absolute_url'):
            context[self.up_name] = '%s%s/%s/' % (obj.get_absolute_url(), _('rate'), _('up'))
            context[self.down_name] = '%s%s/%s/' % (obj.get_absolute_url(), _('rate'), _('down'))
        elif obj:
            ct = ContentType.objects.get_for_model(obj)
            context[self.form_name] = RateForm(initial={'content_type' : ct.id, 'target' : obj._get_pk_val()})
            context[self.up_name] = reverse('rate_up')
            context[self.down_name] = reverse('rate_down')
        return ''

class RateUrlNode(template.Node):
    def __init__(self, object, url_var_name, form_name=None):
        self.object = object
        self.url_var_name =url_var_name
        self.form_name = form_name

    def render(self, context):
        obj = template.Variable(self.object).resolve(context)
        if obj and hasattr(obj, 'get_absolute_url'):
            context[self.url_var_name] = '%s%s/' % (obj.get_absolute_url(), slugify(_('rate by value')))
        elif obj:
            ct = ContentType.objects.get_for_model(obj)
            context[self.form_name] = RateForm(initial={'content_type' : ct.id, 'target' : obj._get_pk_val()})
            context[self.url_var_name] = reverse('rate')
        return ''

@register.tag('rate_urls')
def do_rate_urls(parser, token):
    """
    Generate absolute urls for rating the given model up or down and store them in context.

    Usage::

        {% rate_urls for OBJ as  var_up var_down %}

        {% rate_urls for OBJ as my_form var_up var_down %}

    Examples::

        {% rate_urls for object as url_up url_down %}
        <form action="{{url_up}}" method="POST"><input type="submit" value="+"></form>
        <form action="{{url_down}}" method="POST"><input type="submit" value="-"></form>

        {% rate_urls for object as rate_form url_up url_down %}
        <form action="{{url_up}}" method="POST">{{rate_form}}<input type="submit" value="+"></form>
        <form action="{{url_down}}" method="POST">{{rate_form}}<input type="submit" value="-"></form>
    """
    bits = token.split_contents()
    if (len(bits) != 6 and len(bits) != 7) or bits[1] != 'for' or bits[3] != 'as':
        raise template.TemplateSyntaxError, "%r .... TODO ....." % token.contents.split()[0]
    if len(bits) == 6:
        return RateUrlsNode(bits[2], bits[4], bits[5])
    else:
        return RateUrlsNode(bits[2], bits[5], bits[6], bits[4])

@register.tag
def rate_url(parser, token):
    """
    Fills template variable specified in argument ``tpl_var`` with URL for sending rating value.

    Usage::

        {% rate_url for object as tpl_var %}

    Example::

        {% rate_url for object as r_url %}
        <form action="{{r_url}}" method="POST">
            <input type="text" name="rating" value="0"/>
            <input type="submit" value="Rate it"/>
        </form>
    """
    bits = token.split_contents()
    if len(bits) != 5:
        raise template.TemplateSyntaxError('rate_rul template tag should be used like this: {% rate_url for object as tpl_var %}')
    return RateUrlNode(bits[2], bits[4])

class RatingNode(template.Node):
    def __init__(self, object, name):
        self.object, self.name =  object, name

    def render(self, context):
        obj = template.Variable(self.object).resolve(context)
        if obj:
            context[self.name] = TotalRate.objects.get_total_rating(obj)
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
        context[self.name] = TotalRate.objects.get_top_objects(self.count, self.mods)
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
